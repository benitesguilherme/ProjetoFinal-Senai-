"""
====================================================================
CineSENAI & Teatro - Sistema de Gestão de Bilheteria e Bomboniere
Projeto Final de Curso SENAI
Autores: O Usuário e Sandro
====================================================================
"""

import os
import io
import random
import string
import base64
import secrets
import re
import json
import sqlite3
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, flash, abort, send_file
)
import qrcode

from database.db import get_db, check_and_init_db
from database.seed import init_db

app = Flask(__name__)
app.secret_key = os.environ.get("CINESENAI_SECRET", secrets.token_hex(32))
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

# Garante inicialização do banco de dados na inicialização da aplicação
with app.app_context():
    check_and_init_db()
    if not os.environ.get("CINESENAI_TESTING"):
        from database.catalog import prepare_catalog
        with get_db() as catalog_conn:
            prepare_catalog(catalog_conn)
        catalog_conn.close()

# ====================================================================
# Filtros de Template Customizados (Jinja2)
# ====================================================================

@app.template_filter("moeda")
def format_moeda(val):
    """Formata valor float para moeda brasileira (R$ 00,00)."""
    try:
        val = float(val)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

@app.template_filter("data_br")
def format_data_br(val):
    """Formata data ISO para formato brasileiro DD/MM/AAAA HH:MM."""
    try:
        dt = datetime.strptime(str(val)[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return str(val)

@app.template_filter("hora_br")
def format_hora_br(val):
    """Retorna apenas a hora formatada HH:MM."""
    try:
        dt = datetime.strptime(str(val)[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%H:%M")
    except Exception:
        return str(val)

@app.template_filter("dia_mes_br")
def format_dia_mes_br(val):
    """Retorna dia e mês com nome do dia."""
    dias_semana = {
        0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui",
        4: "Sex", 5: "Sáb", 6: "Dom"
    }
    try:
        dt = datetime.strptime(str(val)[:10], "%Y-%m-%d")
        return f"{dt.strftime('%d/%m')} ({dias_semana[dt.weekday()]})"
    except Exception:
        return str(val)

# Helper para gerar QR Code em base64
def gerar_qr_code_base64(conteudo):
    """Gera uma string base64 PNG de um QR Code."""
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=2,
    )
    qr.add_data(conteudo)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#111111", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def gerar_codigo_localizador(tipo="CINE"):
    """Gera um código localizador único elegante (Ex: CINE-84920)."""
    sufixo = secrets.token_hex(8).upper()
    return f"{tipo}-{sufixo}"

# ====================================================================
# Rotas Principais do Cliente
# ====================================================================

@app.route("/")
def index():
    """Página inicial com catálogo de Cinema e Teatro, destaques e busca."""
    categoria_slug = request.args.get("categoria", "todos")
    busca = request.args.get("q", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    # Categorias para as abas
    cursor.execute("SELECT * FROM categorias ORDER BY id")
    categorias = cursor.fetchall()

    # Destaques para o Hero Banner
    cursor.execute(
        """
        SELECT e.*, c.nome as categoria_nome, c.slug as categoria_slug
        FROM eventos e
        JOIN categorias c ON e.categoria_id = c.id
        WHERE e.em_destaque = 1 AND e.status = 'em_cartaz'
        ORDER BY e.id ASC
        """
    )
    destaques = cursor.fetchall()

    # Query dos eventos filtrados
    query = """
        SELECT e.*, c.nome as categoria_nome, c.slug as categoria_slug,
               (SELECT COUNT(*) FROM sessoes s WHERE s.evento_id = e.id AND s.ativa = 1 AND s.data_hora > datetime('now','localtime')) as total_sessoes
        FROM eventos e
        JOIN categorias c ON e.categoria_id = c.id
        WHERE e.status = 'em_cartaz'
    """
    params = []

    if categoria_slug and categoria_slug != "todos":
        query += " AND c.slug = ?"
        params.append(categoria_slug)

    if busca:
        query += " AND (e.titulo LIKE ? OR e.genero LIKE ? OR e.diretor LIKE ?)"
        busca_param = f"%{busca}%"
        params.extend([busca_param, busca_param, busca_param])

    query += " ORDER BY e.categoria_id ASC, e.em_destaque DESC, e.id ASC"

    cursor.execute(query, params)
    eventos = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        categorias=categorias,
        destaques=destaques,
        eventos=eventos,
        categoria_ativa=categoria_slug,
        busca=busca
    )

@app.route('/bomboniere')
def bomboniere_catalogo():
    conn = get_db()
    produtos = conn.execute('SELECT * FROM produtos_bomboniere WHERE disponivel=1 ORDER BY destaque DESC, categoria, preco').fetchall()
    conn.close()
    return render_template('combos.html', produtos=produtos)

@app.route('/informacoes')
def informacoes():
    return render_template('informacoes.html')

@app.route('/projeto/')
def caderno_projeto():
    return send_file(os.path.join(app.root_path, 'docs', 'ENTREGA.html'))

@app.route('/projeto/DER.svg')
def diagrama_projeto():
    return send_file(os.path.join(app.root_path, 'docs', 'DER.svg'))

@app.route('/meus-ingressos', methods=['GET', 'POST'])
def meus_ingressos():
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip().upper().lstrip('#')
        email = request.form.get('email', '').strip().lower()
        conn = get_db()
        venda = conn.execute('''SELECT v.codigo_localizador FROM vendas v
            JOIN clientes c ON c.id=v.cliente_id
            WHERE v.codigo_localizador=? AND lower(c.email)=?''', (codigo, email)).fetchone()
        conn.close()
        if venda:
            return redirect(url_for('confirmacao', codigo_localizador=venda['codigo_localizador']))
        flash('Não encontramos esse pedido. Confira o localizador e o e-mail.', 'warning')
    return render_template('meus_ingressos.html')

@app.route("/evento/<int:evento_id>")
def evento_detalhes(evento_id):
    """Página de detalhes do filme ou peça com sinopse, trailer e horários das sessões."""
    conn = get_db()
    cursor = conn.cursor()

    # Dados do evento
    cursor.execute(
        """
        SELECT e.*, c.nome as categoria_nome, c.slug as categoria_slug
        FROM eventos e
        JOIN categorias c ON e.categoria_id = c.id
        WHERE e.id = ?
        """,
        (evento_id,)
    )
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        abort(404)

    # Sessões disponíveis agrupadas por data
    cursor.execute(
        """
        SELECT s.*, sa.nome as sala_nome, sa.tipo as sala_tipo,
               DATE(s.data_hora) as data_apenas
        FROM sessoes s
        JOIN salas sa ON s.sala_id = sa.id
        WHERE s.evento_id = ? AND s.ativa = 1 AND s.data_hora > datetime('now','localtime')
        ORDER BY s.data_hora ASC
        """,
        (evento_id,)
    )
    sessoes_raw = cursor.fetchall()

    # Agrupa por data
    sessoes_por_data = {}
    for sessao in sessoes_raw:
        dt = sessao["data_apenas"]
        if dt not in sessoes_por_data:
            sessoes_por_data[dt] = []
        sessoes_por_data[dt].append(sessao)

    conn.close()

    return render_template(
        "evento_detalhe.html",
        evento=evento,
        sessoes_por_data=sessoes_por_data
    )

@app.route("/sessao/<int:sessao_id>/assentos")
def sessao_assentos(sessao_id):
    """Mapa interativo de seleção de assentos."""
    conn = get_db()
    cursor = conn.cursor()

    # Informações da Sessão, Evento e Sala
    cursor.execute(
        """
        SELECT s.*, e.titulo as evento_titulo, e.classificacao, e.duracao, e.poster_url,
               c.nome as categoria_nome, sa.nome as sala_nome, sa.tipo as sala_tipo,
               sa.total_fileiras, sa.assentos_por_fileira
        FROM sessoes s
        JOIN eventos e ON s.evento_id = e.id
        JOIN categorias c ON e.categoria_id = c.id
        JOIN salas sa ON s.sala_id = sa.id
        WHERE s.id = ? AND s.ativa = 1 AND s.data_hora > datetime('now','localtime')
        """,
        (sessao_id,)
    )
    sessao = cursor.fetchone()

    if not sessao:
        conn.close()
        abort(404)

    # Assentos da sala
    cursor.execute(
        """
        SELECT a.*,
               CASE WHEN i.id IS NOT NULL THEN 1 ELSE 0 END as ocupado
        FROM assentos a
        LEFT JOIN ingressos i ON i.assento_id = a.id AND i.sessao_id = ?
        WHERE a.sala_id = ? AND a.ativo = 1
        ORDER BY a.fileira ASC, a.numero ASC
        """,
        (sessao_id, sessao["sala_id"])
    )
    assentos_raw = cursor.fetchall()

    # Organiza assentos em um dicionário por fileira e calcula ocupação
    grid_assentos = {}
    total_assentos = len(assentos_raw)
    assentos_ocupados = 0

    for a in assentos_raw:
        if a["ocupado"] == 1:
            assentos_ocupados += 1
        f = a["fileira"]
        if f not in grid_assentos:
            grid_assentos[f] = []
        grid_assentos[f].append(dict(a))

    sessao_esgotada = (total_assentos > 0 and assentos_ocupados >= total_assentos)

    conn.close()

    return render_template(
        "assentos.html",
        sessao=sessao,
        grid_assentos=grid_assentos,
        total_assentos=total_assentos,
        assentos_ocupados=assentos_ocupados,
        sessao_esgotada=sessao_esgotada
    )

@app.route("/sessao/<int:sessao_id>/bomboniere", methods=["GET", "POST"])
def sessao_bomboniere(sessao_id):
    """Página de seleção de combos de pipoca, doces e bebidas."""
    # Recebe os assentos selecionados passados via query string ou POST
    assentos_ids = request.values.get("assentos_selecionados", "").strip()
    tipos_ingressos = request.values.get("tipos_ingressos", "").strip()

    # Validação: impede entrar na bomboniere sem selecionar assento
    if not assentos_ids:
        flash("Por favor, selecione ao menos uma poltrona no mapa antes de escolher os combos da bomboniere.", "warning")
        return redirect(url_for("sessao_assentos", sessao_id=sessao_id))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT s.*, e.titulo as evento_titulo, e.poster_url, sa.nome as sala_nome
        FROM sessoes s
        JOIN eventos e ON s.evento_id = e.id
        JOIN salas sa ON s.sala_id = sa.id
        WHERE s.id = ?
        """,
        (sessao_id,)
    )
    sessao = cursor.fetchone()

    if not sessao:
        conn.close()
        abort(404)

    # Produtos disponíveis
    cursor.execute(
        "SELECT * FROM produtos_bomboniere WHERE disponivel = 1 ORDER BY destaque DESC, categoria ASC, preco ASC"
    )
    produtos = cursor.fetchall()

    # Agrupa produtos por categoria
    produtos_por_categoria = {}
    for p in produtos:
        cat = p["categoria"]
        if cat not in produtos_por_categoria:
            produtos_por_categoria[cat] = []
        produtos_por_categoria[cat].append(p)

    conn.close()

    return render_template(
        "bomboniere.html",
        sessao=sessao,
        produtos_por_categoria=produtos_por_categoria,
        produtos=produtos,
        assentos_ids=assentos_ids,
        tipos_ingressos=tipos_ingressos
    )

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    """Tela de conferência e pagamento simulado (PIX, Cartão, Balcão)."""
    sessao_id = request.values.get("sessao_id")
    assentos_ids_str = request.values.get("assentos_ids", "")
    tipos_ingressos_str = request.values.get("tipos_ingressos", "")
    itens_bomboniere_str = request.values.get("itens_bomboniere", "")

    if not sessao_id or not assentos_ids_str:
        flash("Sessão ou assentos inválidos. Por favor, reinicie a seleção.", "danger")
        return redirect(url_for("index"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT s.*, e.titulo as evento_titulo, e.poster_url, e.classificacao, sa.nome as sala_nome
        FROM sessoes s
        JOIN eventos e ON s.evento_id = e.id
        JOIN salas sa ON s.sala_id = sa.id
        WHERE s.id = ?
        """,
        (sessao_id,)
    )
    sessao = cursor.fetchone()

    if not sessao:
        conn.close()
        abort(404)

    # Detalha os assentos e calcula preços
    try:
        ids_lista = [int(i.strip()) for i in assentos_ids_str.split(",") if i.strip()]
        if not 1 <= len(ids_lista) <= 8 or len(set(ids_lista)) != len(ids_lista):
            raise ValueError()
    except ValueError:
        conn.close()
        abort(400, description="Seleção de assentos inválida.")
    tipos_lista = [t.strip().upper() for t in tipos_ingressos_str.split(",") if t.strip()]

    if len(tipos_lista) < len(ids_lista):
        tipos_lista.extend(["INTEIRA"] * (len(ids_lista) - len(tipos_lista)))

    placeholders = ",".join(["?"] * len(ids_lista))
    cursor.execute(
        f"SELECT * FROM assentos WHERE id IN ({placeholders}) ORDER BY codigo ASC",
        ids_lista
    )
    assentos_db = {a["id"]: a for a in cursor.fetchall()}
    if (not sessao["ativa"] or sessao["data_hora"] <= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        or len(assentos_db) != len(ids_lista)
        or any(a["sala_id"] != sessao["sala_id"] or not a["ativo"] for a in assentos_db.values())
        or any(t not in ("INTEIRA", "MEIA") for t in tipos_lista)):
        conn.close()
        abort(400, description="A seleção não corresponde a uma sessão disponível.")

    ingressos_detalhe = []
    total_ingressos = 0.0

    for idx, assento_id in enumerate(ids_lista):
        if assento_id in assentos_db:
            assento = assentos_db[assento_id]
            tipo = tipos_lista[idx] if idx < len(tipos_lista) else "INTEIRA"
            preco = sessao["preco_base"] if tipo == "INTEIRA" else (sessao["preco_base"] * 0.5)
            ingressos_detalhe.append({
                "assento_id": assento_id,
                "codigo": assento["codigo"],
                "fileira": assento["fileira"],
                "numero": assento["numero"],
                "tipo_ingresso": tipo,
                "preco": preco
            })
            total_ingressos += preco

    # Detalha itens da bomboniere
    bomboniere_detalhe = []
    total_bomboniere = 0.0

    if itens_bomboniere_str:
        # Formato esperado: prod_id:qtd,prod_id:qtd
        for par in itens_bomboniere_str.split(","):
            if ":" in par:
                try:
                    pid, qtd = map(int, par.strip().split(":"))
                    if qtd > 0:
                        cursor.execute("SELECT * FROM produtos_bomboniere WHERE id = ?", (pid,))
                        p = cursor.fetchone()
                        if p:
                            sub = p["preco"] * qtd
                            bomboniere_detalhe.append({
                                "produto_id": pid,
                                "nome": p["nome"],
                                "preco": p["preco"],
                                "quantidade": qtd,
                                "subtotal": sub
                            })
                            total_bomboniere += sub
                except ValueError:
                    pass

    total_geral = total_ingressos + total_bomboniere

    conn.close()

    # Mock dados PIX
    pix_chave_aleatoria = "SIMULACAO-SEM-VALOR-FINANCEIRO-" + secrets.token_hex(8).upper()
    pix_qr_base64 = gerar_qr_code_base64(pix_chave_aleatoria)

    return render_template(
        "checkout.html",
        sessao=sessao,
        ingressos_detalhe=ingressos_detalhe,
        bomboniere_detalhe=bomboniere_detalhe,
        total_ingressos=total_ingressos,
        total_bomboniere=total_bomboniere,
        total_geral=total_geral,
        assentos_ids_str=assentos_ids_str,
        tipos_ingressos_str=tipos_ingressos_str,
        itens_bomboniere_str=itens_bomboniere_str,
        pix_chave=pix_chave_aleatoria,
        pix_qr_code=pix_qr_base64
    )

@app.route("/confirmacao/<codigo_localizador>")
def confirmacao(codigo_localizador):
    """Página de confirmação e Voucher Digital do Ingresso."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT v.*, c.nome as cliente_nome, c.cpf as cliente_cpf, c.email as cliente_email,
               s.data_hora, s.formato, s.idioma, e.titulo as evento_titulo, e.classificacao,
               e.duracao, e.poster_url, sa.nome as sala_nome, cat.nome as categoria_nome
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN sessoes s ON v.sessao_id = s.id
        JOIN eventos e ON s.evento_id = e.id
        JOIN categorias cat ON e.categoria_id = cat.id
        JOIN salas sa ON s.sala_id = sa.id
        WHERE v.codigo_localizador = ?
        """,
        (codigo_localizador,)
    )
    venda = cursor.fetchone()

    if not venda:
        conn.close()
        abort(404)

    # Ingressos da venda
    cursor.execute(
        """
        SELECT i.*, a.codigo as assento_codigo, a.fileira, a.numero, a.tipo_assento
        FROM ingressos i
        JOIN assentos a ON i.assento_id = a.id
        WHERE i.venda_id = ?
        ORDER BY a.codigo ASC
        """,
        (venda["id"],)
    )
    ingressos = cursor.fetchall()

    # Itens de bomboniere da venda
    cursor.execute(
        """
        SELECT iv.*, p.nome as produto_nome, p.imagem_url
        FROM itens_venda_bomboniere iv
        JOIN produtos_bomboniere p ON iv.produto_id = p.id
        WHERE iv.venda_id = ?
        """,
        (venda["id"],)
    )
    itens_bomboniere = cursor.fetchall()

    conn.close()

    # Gera QR Code do Voucher
    qr_code_voucher = gerar_qr_code_base64(f"CINESENAI-DEMONSTRACAO:{codigo_localizador}")

    return render_template(
        "confirmacao.html",
        venda=venda,
        ingressos=ingressos,
        itens_bomboniere=itens_bomboniere,
        qr_code_voucher=qr_code_voucher
    )

# ====================================================================
# Endpoints da API REST (AJAX e Concorrência Atômica)
# ====================================================================

@app.route("/api/sessao/<int:sessao_id>/assentos")
def api_sessao_assentos(sessao_id):
    """Retorna status atual de todos os assentos da sessão para atualização em tempo real."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT sala_id FROM sessoes WHERE id = ?", (sessao_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"erro": "Sessão não encontrada"}), 404

    sala_id = row["sala_id"]

    cursor.execute(
        """
        SELECT a.id, a.fileira, a.numero, a.codigo, a.tipo_assento,
               CASE WHEN i.id IS NOT NULL THEN 1 ELSE 0 END as ocupado
        FROM assentos a
        LEFT JOIN ingressos i ON i.assento_id = a.id AND i.sessao_id = ?
        WHERE a.sala_id = ? AND a.ativo = 1
        ORDER BY a.fileira ASC, a.numero ASC
        """,
        (sessao_id, sala_id)
    )
    assentos = [dict(a) for a in cursor.fetchall()]

    conn.close()
    return jsonify({
        "sessao_id": sessao_id,
        "assentos": assentos
    })

@app.route("/api/finalizar-compra", methods=["POST"])
def api_finalizar_compra():
    """
    Processa a venda com validação estrita anti-concorrência.
    Se qualquer assento tiver sido reservado por outro cliente concorrentemente,
    a transação é revertida (rollback) e o cliente é notificado.
    """
    dados = request.get_json(silent=True) or request.form.to_dict()
    if not isinstance(dados, dict):
        return jsonify(sucesso=False, mensagem="Pedido inválido."), 400
    for field in ("nome", "cpf", "email", "telefone"):
        if not isinstance(dados.get(field, ""), str):
            return jsonify(sucesso=False, mensagem="Dados cadastrais inválidos."), 400

    sessao_id = dados.get("sessao_id")
    nome = dados.get("nome", "").strip()
    cpf = dados.get("cpf", "").strip()
    email = dados.get("email", "").strip()
    telefone = dados.get("telefone", "").strip()
    forma_pagamento = dados.get("forma_pagamento", "PIX")

    assentos_req = dados.get("assentos", []) # lista de dicts ou string separada
    bomboniere_req = dados.get("bomboniere", [])

    if not sessao_id or not nome or not cpf or not email:
        return jsonify({"sucesso": False, "mensagem": "Dados cadastrais incompletos."}), 400

    if forma_pagamento not in ("PIX", "CARTAO_CREDITO", "BALCAO"):
        return jsonify(sucesso=False, mensagem="Forma de pagamento inválida."), 400
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11 or len(nome) < 3 or len(nome) > 120 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return jsonify(sucesso=False, mensagem="Confira o nome, o CPF de 11 dígitos e o e-mail."), 400
    try:
        sessao_id = int(sessao_id)
        if isinstance(assentos_req, str):
            assentos_req = json.loads(assentos_req)
        if isinstance(bomboniere_req, str):
            bomboniere_req = json.loads(bomboniere_req)
        if not isinstance(assentos_req, list) or not 1 <= len(assentos_req) <= 8:
            raise ValueError()
        if not isinstance(bomboniere_req, list) or len(bomboniere_req) > 30:
            raise ValueError()
        ids = [int(a['assento_id']) for a in assentos_req]
        if len(ids) != len(set(ids)) or any(a.get('tipo_ingresso', 'INTEIRA') not in ('INTEIRA', 'MEIA') for a in assentos_req):
            raise ValueError()
        product_ids = []
        for b in bomboniere_req:
            if isinstance(b['quantidade'], bool) or not str(b['quantidade']).isdigit() or not 1 <= int(b['quantidade']) <= 20:
                raise ValueError()
            product_ids.append(int(b['produto_id']))
        if len(set(product_ids)) != len(product_ids):
            raise ValueError()
    except (ValueError, TypeError, KeyError, AttributeError):
        return jsonify(sucesso=False, mensagem="Selecione até 8 lugares distintos e quantidades válidas de produtos."), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Inicia transação explícita
        cursor.execute("BEGIN IMMEDIATE")

        # 1. Verifica se a sessão existe e está ativa
        cursor.execute(
            """
            SELECT s.*, e.categoria_id, cat.slug as cat_slug
            FROM sessoes s
            JOIN eventos e ON s.evento_id = e.id
            JOIN categorias cat ON e.categoria_id = cat.id
            WHERE s.id = ? AND s.ativa = 1 AND s.data_hora > datetime('now','localtime')
            """,
            (sessao_id,)
        )
        sessao = cursor.fetchone()
        if not sessao:
            conn.rollback()
            conn.close()
            return jsonify({"sucesso": False, "mensagem": "Sessão inválida ou inativa."}), 404

        # 2. Converte e valida assentos solicitados
        if isinstance(assentos_req, str):
            import json
            try:
                assentos_req = json.loads(assentos_req)
            except Exception:
                assentos_req = []

        if not assentos_req:
            conn.rollback()
            conn.close()
            return jsonify({"sucesso": False, "mensagem": "Nenhum assento selecionado."}), 400

        assentos_ids = [int(a["assento_id"]) for a in assentos_req]

        placeholders_seats = ','.join('?' for _ in assentos_ids)
        valid_seats = cursor.execute(f'SELECT COUNT(*) FROM assentos WHERE sala_id=? AND ativo=1 AND id IN ({placeholders_seats})', [sessao['sala_id']] + assentos_ids).fetchone()[0]
        if valid_seats != len(assentos_ids):
            raise ValueError("Uma poltrona não pertence a esta sala ou está indisponível.")

        # 3. VALIDAÇÃO ANTI-CONCORRÊNCIA: Verifica se algum assento já foi comprado nesta sessão
        placeholders = ",".join(["?"] * len(assentos_ids))
        cursor.execute(
            f"""
            SELECT a.codigo
            FROM ingressos i
            JOIN assentos a ON i.assento_id = a.id
            WHERE i.sessao_id = ? AND i.assento_id IN ({placeholders})
            """,
            [sessao_id] + assentos_ids
        )
        ocupados = cursor.fetchall()

        if ocupados:
            codigos_conflito = ", ".join([r["codigo"] for r in ocupados])
            conn.rollback()
            conn.close()
            return jsonify({
                "sucesso": False,
                "mensagem": f"Ops! Os seguintes assentos acabaram de ser reservados por outro cliente: {codigos_conflito}. Por favor, escolha outros lugares."
            }), 409

        # 4. Cadastra ou Atualiza Cliente
        cursor.execute("SELECT id FROM clientes WHERE cpf = ?", (cpf,))
        cliente_row = cursor.fetchone()
        if cliente_row:
            cliente_id = cliente_row["id"]
            cursor.execute(
                "UPDATE clientes SET nome = ?, email = ?, telefone = ? WHERE id = ?",
                (nome, email, telefone, cliente_id)
            )
        else:
            cursor.execute(
                "INSERT INTO clientes (nome, cpf, email, telefone) VALUES (?, ?, ?, ?)",
                (nome, cpf, email, telefone)
            )
            cliente_id = cursor.lastrowid

        # 5. Calcula Totais
        total_ingressos = 0.0
        ingressos_inserir = []

        for item in assentos_req:
            aid = int(item["assento_id"])
            tipo = item.get("tipo_ingresso", "INTEIRA").upper()
            preco = float(sessao["preco_base"]) if tipo == "INTEIRA" else float(sessao["preco_base"] * 0.5)
            total_ingressos += preco
            ingressos_inserir.append((sessao_id, aid, tipo, preco))

        # Calcula Bomboniere
        if isinstance(bomboniere_req, str):
            import json
            try:
                bomboniere_req = json.loads(bomboniere_req)
            except Exception:
                bomboniere_req = []

        total_bomboniere = 0.0
        itens_bomboniere_inserir = []

        for bitem in bomboniere_req:
            pid = int(bitem["produto_id"])
            qtd = int(bitem["quantidade"])
            if qtd > 0:
                cursor.execute("SELECT preco FROM produtos_bomboniere WHERE id = ? AND disponivel = 1", (pid,))
                prod = cursor.fetchone()
                if not prod:
                    raise ValueError("Produto indisponível. Revise seu combo.")
                if prod:
                    sub = float(prod["preco"]) * qtd
                    total_bomboniere += sub
                    itens_bomboniere_inserir.append((pid, qtd, float(prod["preco"]), sub))

        total_geral = total_ingressos + total_bomboniere

        # 6. Cria Código Localizador Único
        prefixo = "TEATRO" if sessao["cat_slug"] == "teatro" else "CINE"
        codigo_localizador = gerar_codigo_localizador(prefixo)

        # 7. Registra Venda
        cursor.execute(
            """
            INSERT INTO vendas
            (cliente_id, sessao_id, codigo_localizador, data_venda, total_ingressos, total_bomboniere, total_geral, forma_pagamento, status)
            VALUES (?, ?, ?, datetime('now','localtime'), ?, ?, ?, ?, ?)
            """,
            (cliente_id, sessao_id, codigo_localizador, total_ingressos, total_bomboniere, total_geral, forma_pagamento, "PENDENTE" if forma_pagamento == "BALCAO" else "APROVADO")
        )
        venda_id = cursor.lastrowid

        # 8. Registra Ingressos
        for sid, aid, tipo, preco in ingressos_inserir:
            cursor.execute(
                """
                INSERT INTO ingressos (venda_id, sessao_id, assento_id, tipo_ingresso, preco)
                VALUES (?, ?, ?, ?, ?)
                """,
                (venda_id, sid, aid, tipo, preco)
            )

        # 9. Registra Itens de Bomboniere
        for pid, qtd, p_unit, sub in itens_bomboniere_inserir:
            cursor.execute(
                """
                INSERT INTO itens_venda_bomboniere (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
                """,
                (venda_id, pid, qtd, p_unit, sub)
            )

        conn.commit()
        conn.close()

        return jsonify({
            "sucesso": True,
            "codigo_localizador": codigo_localizador,
            "redirect_url": url_for("confirmacao", codigo_localizador=codigo_localizador)
        })

    except ValueError as e:
        conn.rollback()
        conn.close()
        return jsonify(sucesso=False, mensagem=str(e)), 400
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return jsonify(sucesso=False, mensagem="Este lugar acabou de ser ocupado. Escolha outro assento."), 409
    except Exception:
        conn.rollback()
        conn.close()
        app.logger.exception("Falha ao finalizar pedido")
        return jsonify(sucesso=False, mensagem="Não foi possível concluir. Tente novamente."), 500

# ====================================================================
# Painel Administrativo / Gestão
# ====================================================================

@app.route("/admin")
def admin_dashboard():
    """Painel Administrativo para acompanhamento de vendas, ocupação e gestão."""
    conn = get_db()
    cursor = conn.cursor()

    # Métricas Gerais
    cursor.execute("SELECT COUNT(*) FROM vendas WHERE status = 'APROVADO'")
    total_vendas_count = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(total_geral), 0) FROM vendas WHERE status = 'APROVADO'")
    faturamento_total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ingressos")
    total_ingressos_vendidos = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM itens_venda_bomboniere")
    total_itens_bomboniere = cursor.fetchone()[0]

    # Lista de Todas as Vendas Recentes
    cursor.execute(
        """
        SELECT v.*, c.nome as cliente_nome, c.email as cliente_email,
               e.titulo as evento_titulo, sa.nome as sala_nome, s.data_hora,
               (SELECT COUNT(*) FROM ingressos i WHERE i.venda_id = v.id) as qtd_ingressos,
               (SELECT COALESCE(SUM(quantidade), 0) FROM itens_venda_bomboniere iv WHERE iv.venda_id = v.id) as qtd_bomboniere
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN sessoes s ON v.sessao_id = s.id
        JOIN eventos e ON s.evento_id = e.id
        JOIN salas sa ON s.sala_id = sa.id
        ORDER BY v.data_venda DESC
        """
    )
    vendas = cursor.fetchall()

    # Estatísticas de Ocupação por Sessão
    cursor.execute(
        """
        SELECT s.id as sessao_id, s.data_hora, s.formato, s.idioma, s.preco_base,
               e.titulo as evento_titulo, sa.nome as sala_nome, sa.capacidade,
               COUNT(i.id) as ingressos_vendidos,
               ROUND((CAST(COUNT(i.id) AS REAL) / sa.capacidade) * 100, 1) as taxa_ocupacao
        FROM sessoes s
        JOIN eventos e ON s.evento_id = e.id
        JOIN salas sa ON s.sala_id = sa.id
        LEFT JOIN ingressos i ON i.sessao_id = s.id
        GROUP BY s.id
        ORDER BY s.data_hora ASC
        """
    )
    sessoes_stats = cursor.fetchall()

    # Média de taxa de ocupação
    taxa_ocupacao_media = 0.0
    if sessoes_stats:
        total_taxas = sum(s["taxa_ocupacao"] for s in sessoes_stats)
        taxa_ocupacao_media = round(total_taxas / len(sessoes_stats), 1)

    # Eventos e Salas para o formulário de nova sessão e gestão
    cursor.execute(
        """
        SELECT e.*, c.nome as categoria_nome,
               (SELECT COUNT(*) FROM sessoes s WHERE s.evento_id = e.id) as total_sessoes
        FROM eventos e
        JOIN categorias c ON e.categoria_id = c.id
        ORDER BY e.id DESC
        """
    )
    todos_eventos = cursor.fetchall()

    cursor.execute("SELECT id, titulo FROM eventos WHERE status = 'em_cartaz' ORDER BY titulo ASC")
    eventos_lista = cursor.fetchall()

    cursor.execute("SELECT id, nome, tipo FROM salas ORDER BY id ASC")
    salas_lista = cursor.fetchall()

    cursor.execute("SELECT * FROM categorias ORDER BY id ASC")
    todas_categorias = cursor.fetchall()

    # Todas as sessões detalhadas para gestão
    cursor.execute(
        """
        SELECT s.*, e.titulo as evento_titulo, sa.nome as sala_nome, sa.capacidade,
               (SELECT COUNT(*) FROM ingressos i WHERE i.sessao_id = s.id) as ingressos_vendidos
        FROM sessoes s
        JOIN eventos e ON s.evento_id = e.id
        JOIN salas sa ON s.sala_id = sa.id
        ORDER BY s.data_hora DESC
        """
    )
    todas_sessoes = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_vendas_count=total_vendas_count,
        faturamento_total=faturamento_total,
        total_ingressos_vendidos=total_ingressos_vendidos,
        total_itens_bomboniere=total_itens_bomboniere,
        taxa_ocupacao_media=taxa_ocupacao_media,
        vendas=vendas,
        sessoes_stats=sessoes_stats,
        eventos_lista=eventos_lista,
        salas_lista=salas_lista,
        todos_eventos=todos_eventos,
        todas_categorias=todas_categorias,
        todas_sessoes=todas_sessoes
    )

@app.route("/admin/evento/novo", methods=["POST"])
def admin_novo_evento():
    """Cadastra um novo filme ou espetáculo no catálogo a partir do painel administrativo."""
    categoria_id = request.form.get("categoria_id")
    titulo = request.form.get("titulo", "").strip()
    titulo_original = request.form.get("titulo_original", "").strip()
    sinopse = request.form.get("sinopse", "").strip()
    classificacao = request.form.get("classificacao", "Livre")
    duracao = request.form.get("duracao", 120)
    genero = request.form.get("genero", "").strip()
    diretor = request.form.get("diretor", "").strip()
    elenco = request.form.get("elenco", "").strip()
    poster_url = request.form.get("poster_url", "").strip()
    banner_url = request.form.get("banner_url", "").strip()
    trailer_url = request.form.get("trailer_url", "").strip()
    em_destaque = 1 if request.form.get("em_destaque") else 0
    status = request.form.get("status", "em_cartaz")

    if not titulo or not sinopse or not genero:
        flash("Por favor, preencha ao menos o Título, Gênero e Sinopse da obra.", "warning")
        return redirect(url_for("admin_dashboard"))

    if not poster_url:
        poster_url = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=600&q=80"
    if not banner_url:
        banner_url = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1600&q=80"

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO eventos (
                categoria_id, titulo, titulo_original, sinopse, classificacao,
                duracao, genero, diretor, elenco, banner_url, poster_url,
                trailer_url, em_destaque, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                categoria_id, titulo, titulo_original, sinopse, classificacao,
                int(duracao), genero, diretor, elenco, banner_url, poster_url,
                trailer_url, em_destaque, status
            )
        )
        conn.commit()
        conn.close()
        flash(f"Obra '{titulo}' cadastrada com sucesso no catálogo!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar obra: {str(e)}", "danger")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/evento/<int:evento_id>/status", methods=["POST"])
def admin_evento_status(evento_id):
    """Atualiza o status de exibição de um evento ou o remove."""
    novo_status = request.form.get("status")
    acao = request.form.get("acao", "atualizar")

    conn = get_db()
    cursor = conn.cursor()

    try:
        if acao == "excluir":
            cursor.execute("SELECT COUNT(*) FROM sessoes WHERE evento_id = ?", (evento_id,))
            qtd_sessoes = cursor.fetchone()[0]
            if qtd_sessoes > 0:
                cursor.execute("UPDATE eventos SET status = 'encerrado' WHERE id = ?", (evento_id,))
                flash("A obra possui sessões históricas vinculadas e foi marcada como 'encerrado' para preservar a integridade.", "info")
            else:
                cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
                flash("Obra excluída com sucesso do catálogo!", "success")
        else:
            cursor.execute("UPDATE eventos SET status = ? WHERE id = ?", (novo_status, evento_id))
            flash(f"Status da obra atualizado para '{novo_status}'!", "success")

        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao atualizar obra: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/sessao/nova", methods=["POST"])
def admin_nova_sessao():
    """Cadastra uma nova sessão a partir do painel administrativo."""
    evento_id = request.form.get("evento_id")
    sala_id = request.form.get("sala_id")
    data_hora = request.form.get("data_hora")
    formato = request.form.get("formato", "2D")
    idioma = request.form.get("idioma", "DUB")
    preco_base = request.form.get("preco_base", 40.0)

    conn = None
    try:
        data_hora = datetime.fromisoformat(data_hora).strftime('%Y-%m-%d %H:%M:%S')
        preco_base = float(preco_base)
        if not 0 < preco_base <= 10000 or idioma not in ('DUB', 'LEG', 'NAC'):
            raise ValueError('Preço ou idioma inválido.')
        conn = get_db()
        cursor = conn.cursor()
        evento = cursor.execute('SELECT duracao FROM eventos WHERE id=?', (evento_id,)).fetchone()
        if not evento:
            raise ValueError('Evento não encontrado.')
        conflito = cursor.execute('''SELECT 1 FROM sessoes s JOIN eventos e ON e.id=s.evento_id
            WHERE s.sala_id=? AND s.ativa=1 AND s.data_hora < datetime(?, '+' || ? || ' minutes')
            AND datetime(s.data_hora, '+' || (e.duracao+20) || ' minutes') > ?''',
            (sala_id, data_hora, evento['duracao']+20, data_hora)).fetchone()
        if conflito:
            raise ValueError('A sala já tem uma sessão nesse período. Considere a duração e 20 minutos de intervalo.')
        cursor.execute(
            """
            INSERT INTO sessoes (evento_id, sala_id, data_hora, formato, idioma, preco_base, ativa)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (evento_id, sala_id, data_hora, formato, idioma, float(preco_base))
        )
        conn.commit()
        flash("Nova sessão cadastrada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao cadastrar sessão: {str(e)}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/sessao/<int:sessao_id>/toggle", methods=["POST"])
def admin_sessao_toggle(sessao_id):
    """Alterna a sessão entre ativa e desativada para venda."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE sessoes SET ativa = CASE WHEN ativa = 1 THEN 0 ELSE 1 END WHERE id = ?", (sessao_id,))
        conn.commit()
        flash("Disponibilidade da sessão alternada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao alterar disponibilidade da sessão: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/sessao/<int:sessao_id>/excluir", methods=["POST"])
def admin_sessao_excluir(sessao_id):
    """Exclui ou inativa uma sessão."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM ingressos WHERE sessao_id = ?", (sessao_id,))
        ingressos_vendidos = cursor.fetchone()[0]
        if ingressos_vendidos > 0:
            cursor.execute("UPDATE sessoes SET ativa = 0 WHERE id = ?", (sessao_id,))
            flash("A sessão já possui ingressos vendidos e foi desativada em vez de excluída para manter o histórico financeiro.", "warning")
        else:
            cursor.execute("DELETE FROM sessoes WHERE id = ?", (sessao_id,))
            flash("Sessão excluída com sucesso!", "success")
        conn.commit()
    except Exception as e:
        flash(f"Erro ao excluir sessão: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reset-dados", methods=["POST"])
def admin_reset_dados():
    """Restaura o banco de dados para os dados padrão de demonstração."""
    init_db(force_recreate=True)
    flash("Banco de dados restaurado com sucesso com os dados padrão do SENAI!", "info")
    return redirect(url_for("admin_dashboard"))

# ====================================================================
# Tratamento de Erros
# ====================================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# ====================================================================
# Execução Principal
# ====================================================================

if __name__ == "__main__":
    print("Iniciando CineSENAI & Teatro...")
    print("Acesse em: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
