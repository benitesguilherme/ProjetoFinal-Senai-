"""
Testes Automatizados de Integração e Regras de Negócio
CineSENAI & Teatro
Autores: O Usuário e Sandro
"""

import os
import unittest
import json
import tempfile
from datetime import datetime, timedelta
_test_dir = tempfile.TemporaryDirectory(prefix="cinesenai-tests-")
os.environ["CINESENAI_DB"] = os.path.join(_test_dir.name, "test.db")
os.environ["CINESENAI_TESTING"] = "1"
from app import app
from database.seed import init_db
from database.db import get_db

class CineSenaiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Garante banco inicializado e limpo para testes
        init_db(force_recreate=True)
        with get_db() as conn:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            conn.execute("UPDATE sessoes SET data_hora = ? || substr(data_hora, 11)", (tomorrow,))
        conn.close()
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_pagina_inicial_e_catalogo(self):
        """Verifica se a página inicial carrega os filmes e categorias com sucesso."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("O Jogo da Imitação", html)
        self.assertIn("Oppenheimer", html)
        self.assertIn("Interestelar", html)
        self.assertIn("O Fantasma da Ópera", html)
        self.assertIn("CineSENAI", html)

    def test_02_filtro_categoria_cinema_e_teatro(self):
        """Verifica filtros por categoria."""
        resp_cinema = self.client.get("/?categoria=cinema")
        self.assertEqual(resp_cinema.status_code, 200)
        self.assertIn("O Jogo da Imitação", resp_cinema.data.decode("utf-8"))

        resp_teatro = self.client.get("/?categoria=teatro")
        self.assertEqual(resp_teatro.status_code, 200)
        self.assertIn("O Fantasma da Ópera", resp_teatro.data.decode("utf-8"))

    def test_03_detalhes_do_filme_o_jogo_da_imitacao(self):
        """Verifica a exibição correta dos detalhes de 'O Jogo da Imitação'."""
        response = self.client.get("/evento/1")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("O Jogo da Imitação", html)
        self.assertIn("The Imitation Game", html)
        self.assertIn("Alan Turing", html)
        self.assertIn("Benedict Cumberbatch", html)
        self.assertIn("Horários e Sessões Disponíveis", html)

    def test_04_mapa_de_assentos(self):
        """Verifica se a tela do mapa de assentos carrega a sala e poltronas."""
        response = self.client.get("/sessao/1/assentos")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("TELA - IMAX", html)
        self.assertIn("Subtotal Ingressos", html)
        self.assertIn("btnContinuarBomboniere", html)

    def test_05_api_assentos_json(self):
        """Verifica se a API JSON retorna o status de assentos corretamente."""
        response = self.client.get("/api/sessao/1/assentos")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("assentos", data)
        self.assertGreater(len(data["assentos"]), 0)
        
        # Testa se a sessão 2 tem os assentos pré-ocupados do seed (D5, D6, D7)
        resp_s2 = self.client.get("/api/sessao/2/assentos")
        data_s2 = resp_s2.get_json()
        ocupados = [a["codigo"] for a in data_s2["assentos"] if a["ocupado"] == 1]
        self.assertIn("D5", ocupados)
        self.assertIn("D6", ocupados)
        self.assertIn("D7", ocupados)

    def test_06_pagina_bomboniere(self):
        """Verifica a exibição dos produtos e combos da bomboniere."""
        response = self.client.get("/sessao/1/bomboniere?assentos_selecionados=1,2&tipos_ingressos=INTEIRA,MEIA")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Combo Duplo CineSENAI", html)
        self.assertIn("Pipoca Doce Gourmet", html)
        self.assertIn("Avançar para Pagamento", html)

    def test_07_fluxo_compra_e_anti_concorrencia(self):
        """
        Testa o fluxo completo de compra atômica e garante que assento já comprado
        NÃO pode ser comprado novamente (regra de integridade anti-concorrência).
        """
        # Pega assentos livres na sessão 1
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo FROM assentos WHERE sala_id = 1 AND codigo = 'C4'")
        assento_c4 = cursor.fetchone()
        conn.close()

        payload = {
            "sessao_id": 1,
            "nome": "Marcos Teste Unitario",
            "cpf": "111.222.333-44",
            "email": "marcos@teste.com",
            "telefone": "(11) 91234-5678",
            "forma_pagamento": "PIX",
            "assentos": [
                {"assento_id": assento_c4["id"], "tipo_ingresso": "INTEIRA"}
            ],
            "bomboniere": [
                {"produto_id": 1, "quantidade": 1} # Combo Duplo
            ]
        }

        # Primeira compra: Deve ter sucesso
        response = self.client.post(
            "/api/finalizar-compra",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["sucesso"])
        codigo_localizador = data["codigo_localizador"]
        self.assertTrue(codigo_localizador.startswith("CINE-"))

        # Segunda compra para o MESMO assento na MESMA sessão: Deve falhar com 409 Conflict
        payload_duplicado = {
            "sessao_id": 1,
            "nome": "Outro Cliente Concorrente",
            "cpf": "999.888.777-66",
            "email": "outro@cliente.com",
            "telefone": "(11) 98888-7777",
            "forma_pagamento": "CARTAO_CREDITO",
            "assentos": [
                {"assento_id": assento_c4["id"], "tipo_ingresso": "MEIA"}
            ]
        }

        response_duplicada = self.client.post(
            "/api/finalizar-compra",
            data=json.dumps(payload_duplicado),
            content_type="application/json"
        )
        self.assertEqual(response_duplicada.status_code, 409)
        data_duplicada = response_duplicada.get_json()
        self.assertFalse(data_duplicada["sucesso"])
        self.assertIn("C4", data_duplicada["mensagem"])

    def test_08_pagina_confirmacao_voucher(self):
        """Verifica se a página de confirmação exibe o voucher e QR Code gerado."""
        response = self.client.get("/confirmacao/CINE-84920")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("CINE-84920", html)
        self.assertIn("Carlos Eduardo Silva", html)
        self.assertIn("data:image/png;base64", html) # QR Code Base64
        self.assertIn("Imprimir / Salvar Ingresso", html)

    def test_09_painel_administrativo(self):
        """Verifica o painel administrativo, KPIs de faturamento e ocupação."""
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("Painel Administrativo do CineSENAI", html)
        self.assertIn("Faturamento Total", html)
        self.assertIn("Ocupação Média", html)
        self.assertIn("Histórico de Pedidos e Vendas", html)
        self.assertIn("Gestão das Obras Cadastradas", html)
        self.assertIn("Cadastrar Novo Filme ou Peça Teatral", html)

    def test_10_admin_cadastro_e_gestao_evento(self):
        """Testa o cadastro de uma nova obra no catálogo e a alteração de seu status."""
        novo_evento_data = {
            "categoria_id": 1,
            "titulo": "Matrix Resurrections (Teste)",
            "titulo_original": "The Matrix Resurrections",
            "sinopse": "Uma continuação inovadora com Neo e Trinity no mundo digital.",
            "classificacao": "14",
            "duracao": "148",
            "genero": "Ficção Científica, Ação",
            "diretor": "Lana Wachowski",
            "elenco": "Keanu Reeves, Carrie-Anne Moss",
            "poster_url": "https://example.com/poster.jpg",
            "banner_url": "https://example.com/banner.jpg",
            "trailer_url": "https://youtube.com/embed/test",
            "em_destaque": "1",
            "status": "em_cartaz"
        }

        # 1. Cadastra nova obra
        resp_post = self.client.post("/admin/evento/novo", data=novo_evento_data, follow_redirects=True)
        self.assertEqual(resp_post.status_code, 200)
        html_admin = resp_post.data.decode("utf-8")
        self.assertIn("Matrix Resurrections (Teste)", html_admin)

        # 2. Localiza o ID gerado
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM eventos WHERE titulo = 'Matrix Resurrections (Teste)'")
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        evento_id = row["id"]
        self.assertEqual(row["status"], "em_cartaz")

        # 3. Altera status para 'em_breve'
        resp_status = self.client.post(
            f"/admin/evento/{evento_id}/status",
            data={"status": "em_breve", "acao": "atualizar"},
            follow_redirects=True
        )
        self.assertEqual(resp_status.status_code, 200)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM eventos WHERE id = ?", (evento_id,))
        status_atual = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(status_atual, "em_breve")

        # 4. Exclui a obra de teste
        resp_del = self.client.post(
            f"/admin/evento/{evento_id}/status",
            data={"acao": "excluir"},
            follow_redirects=True
        )
        self.assertEqual(resp_del.status_code, 200)

    def test_11_admin_gestao_sessoes(self):
        """Testa o cadastro, alternância de disponibilidade (ativa/inativa) e exclusão de sessão."""
        nova_sessao_data = {
            "evento_id": 1,
            "sala_id": 2,
            "data_hora": "2026-12-31 22:00",
            "formato": "VIP 2D",
            "idioma": "LEG",
            "preco_base": "55.00"
        }

        # 1. Cria sessão
        resp_nova = self.client.post("/admin/sessao/nova", data=nova_sessao_data, follow_redirects=True)
        self.assertEqual(resp_nova.status_code, 200)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ativa FROM sessoes WHERE data_hora = '2026-12-31 22:00:00'")
        sessao_row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(sessao_row)
        sessao_id = sessao_row["id"]
        self.assertEqual(sessao_row["ativa"], 1)

        # 2. Desativa sessão (pausar)
        resp_toggle = self.client.post(f"/admin/sessao/{sessao_id}/toggle", follow_redirects=True)
        self.assertEqual(resp_toggle.status_code, 200)

        # A sessão pausada deve retornar 404 para compra pelo cliente
        resp_client = self.client.get(f"/sessao/{sessao_id}/assentos")
        self.assertEqual(resp_client.status_code, 404)

        # 3. Exclui sessão sem ingressos
        resp_del = self.client.post(f"/admin/sessao/{sessao_id}/excluir", follow_redirects=True)
        self.assertEqual(resp_del.status_code, 200)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessoes WHERE id = ?", (sessao_id,))
        self.assertIsNone(cursor.fetchone())
        conn.close()

    def test_12_validacao_bomboniere_sem_assentos(self):
        """Verifica se acessar a bomboniere sem selecionar assentos redireciona de volta para o mapa."""
        response = self.client.get("/sessao/1/bomboniere")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/sessao/1/assentos", response.location)

    def test_13_validacao_checkout_api_erros(self):
        """Verifica validações estritas de erro 400 da API de compra."""
        # Payload incompleto (sem nome/cpf/email)
        resp_incompleto = self.client.post(
            "/api/finalizar-compra",
            data=json.dumps({"sessao_id": 1}),
            content_type="application/json"
        )
        self.assertEqual(resp_incompleto.status_code, 400)

        # Payload sem assentos
        resp_sem_assentos = self.client.post(
            "/api/finalizar-compra",
            data=json.dumps({
                "sessao_id": 1,
                "nome": "Teste",
                "cpf": "123.456.789-00",
                "email": "teste@email.com",
                "telefone": "(11) 99999-9999",
                "assentos": []
            }),
            content_type="application/json"
        )
        self.assertEqual(resp_sem_assentos.status_code, 400)

    def test_14_sessao_esgotada_visualizacao(self):
        """Testa se uma sessão com 100% dos assentos ocupados exibe o aviso de esgotada."""
        conn = get_db()
        cursor = conn.cursor()

        # Cria uma sessão teste com 1 assento na sala
        cursor.execute("INSERT INTO sessoes (evento_id, sala_id, data_hora, formato, idioma, preco_base, ativa) VALUES (1, 1, datetime('now', '+2 days'), '2D', 'DUB', 40.0, 1)")
        sess_id = cursor.lastrowid

        # Cria uma venda e ocupa TODOS os assentos da sala 1 para essa sessão
        cursor.execute("INSERT INTO vendas (cliente_id, sessao_id, codigo_localizador, total_ingressos, total_bomboniere, total_geral, forma_pagamento) VALUES (1, ?, 'CINE-TESTE', 100, 0, 100, 'PIX')", (sess_id,))
        venda_id = cursor.lastrowid

        cursor.execute("SELECT id FROM assentos WHERE sala_id = 1")
        all_seats = cursor.fetchall()
        for s in all_seats:
            cursor.execute("INSERT INTO ingressos (venda_id, sessao_id, assento_id, tipo_ingresso, preco) VALUES (?, ?, ?, 'INTEIRA', 40.0)", (venda_id, sess_id, s["id"]))

        conn.commit()
        conn.close()

        # Acessa a tela de assentos da sessão
        response = self.client.get(f"/sessao/{sess_id}/assentos")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")
        self.assertIn("SESSÃO ESGOTADA (100% OCUPADA)", html)

if __name__ == "__main__":
    unittest.main()
