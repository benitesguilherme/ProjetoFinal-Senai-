"""
Módulo de Inicialização e Alimentação do Banco de Dados
CineSENAI & Teatro - Projeto Final SENAI
Autores: O Usuário e Sandro
"""

import os
import sqlite3
from datetime import datetime, timedelta

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("CINESENAI_DB", os.path.join(DB_DIR, "cinema.db"))
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")
SEED_PATH = os.path.join(DB_DIR, "seed.sql")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(force_recreate=False):
    """Cria as tabelas e alimenta com dados iniciais se o banco não existir ou se solicitado."""
    if force_recreate and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Executa o schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # Verifica se já há dados em eventos
    cursor.execute("SELECT COUNT(*) FROM eventos")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_data(conn)

    conn.commit()
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # 1. Categorias
    categorias = [
        (1, "Cinema", "fa-film", "cinema", "Lançamentos e clássicos da sétima arte nas melhores salas"),
        (2, "Teatro", "fa-masks-theater", "teatro", "Grandes espetáculos, musicais e peças consagradas")
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO categorias (id, nome, icone, slug, descricao) VALUES (?, ?, ?, ?, ?)",
        categorias
    )

    # 2. Salas
    salas = [
        (1, "Sala 01 - IMAX Laser 4K", "IMAX", 96, 8, 12),
        (2, "Sala 02 - Dolby Atmos VIP", "VIP", 60, 6, 10),
        (3, "Teatro Municipal SENAI - Palco Nobre", "Teatro", 112, 8, 14)
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO salas (id, nome, tipo, capacidade, total_fileiras, assentos_por_fileira) VALUES (?, ?, ?, ?, ?, ?)",
        salas
    )

    # 3. Gerar Assentos para cada Sala
    # Sala 1: A a H (8 fileiras) x 1 a 12
    # Sala 2: A a F (6 fileiras) x 1 a 10 (todas VIP)
    # Sala 3: A a H (8 fileiras) x 1 a 14 (A e B são VIP; C-G normais; H cadeirante)
    fileiras_letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    for sala_id, nome, tipo, cap, tot_fil, ass_fil in salas:
        for f_idx in range(tot_fil):
            letra = fileiras_letras[f_idx]
            for num in range(1, ass_fil + 1):
                cod = f"{letra}{num}"
                tipo_assento = "PADRAO"

                if tipo == "VIP":
                    tipo_assento = "VIP"
                elif tipo == "Teatro" and letra in ["A", "B"]:
                    tipo_assento = "VIP"
                elif letra == "H" and num in [1, 2, ass_fil - 1, ass_fil]:
                    tipo_assento = "CADEIRANTE"
                elif letra == "A" and num in [1, 2, ass_fil - 1, ass_fil]:
                    tipo_assento = "CADEIRANTE"

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO assentos (sala_id, fileira, numero, codigo, tipo_assento, ativo)
                    VALUES (?, ?, ?, ?, ?, 1)
                    """,
                    (sala_id, letra, num, cod, tipo_assento)
                )

    # 4. Eventos (Filmes e Peças de Teatro)
    eventos = [
        (
            1, 1,
            "O Jogo da Imitação",
            "The Imitation Game",
            "Durante a Segunda Guerra Mundial, o gênio matemático britânico Alan Turing lidera uma equipe ultrassecreta em Bletchley Park para decifrar a temida máquina Enigma nazista. Uma corrida dramática contra o tempo que mudou os rumos da história humana e fundamentou a computação moderna.",
            "12",
            114,
            "Drama, Biografia, História",
            "Morten Tyldum",
            "Benedict Cumberbatch, Keira Knightley, Matthew Goode, Mark Strong",
            "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=600&q=80",
            "https://www.youtube.com/embed/nuPZUUED5uk",
            1,
            "em_cartaz"
        ),
        (
            2, 1,
            "Oppenheimer",
            "Oppenheimer",
            "A fascinante e turbulenta história de J. Robert Oppenheimer, o físico teórico conhecido como o pai da bomba atômica, liderando o Projeto Manhattan sob o peso moral e geopolítico de mudar o destino da civilização humana para sempre.",
            "16",
            180,
            "Biografia, Drama, História",
            "Christopher Nolan",
            "Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr., Florence Pugh",
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=600&q=80",
            "https://www.youtube.com/embed/uYPbbksJxIg",
            1,
            "em_cartaz"
        ),
        (
            3, 1,
            "Interestelar",
            "Interstellar",
            "Em um futuro onde a Terra está à beira do colapso e a fome ameaça a humanidade, um grupo de exploradores e cientistas parte em uma audaciosa missão interestelar através de um buraco de minhoca recém-descoberto, desafiando as leis do tempo e do espaço.",
            "10",
            169,
            "Ficção Científica, Aventura, Drama",
            "Christopher Nolan",
            "Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine",
            "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80",
            "https://www.youtube.com/embed/zSWdZVtXT7E",
            1,
            "em_cartaz"
        ),
        (
            4, 1,
            "Divertida Mente 2",
            "Inside Out 2",
            "De volta à mente da recém-adolescente Riley, o Quartel-General das emoções passa por uma reforma inesperada para abrir espaço para novas e complexas sensações: Ansiedade, Inveja, Tédio e Vergonha chegam para bagunçar a rotina de Alegria, Tristeza, Raiva, Medo e Nojinho.",
            "Livre",
            96,
            "Animação, Comédia, Família",
            "Kelsey Mann",
            "Amy Poehler, Maya Hawke, Phyllis Smith, Lewis Black, Tony Hale",
            "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1513151233558-d860c5398176?auto=format&fit=crop&w=600&q=80",
            "https://www.youtube.com/embed/LEjhY15eCx0",
            1,
            "em_cartaz"
        ),
        (
            5, 1,
            "Duna: Parte 2",
            "Dune: Part Two",
            "Paul Atreides se une a Chani e aos Fremen em busca de vingança contra os conspiradores que destruíram sua família. Diante de uma escolha entre o amor de sua vida e o destino do universo conhecido, ele luta para evitar um futuro terrível que só ele pode prever.",
            "14",
            166,
            "Ficção Científica, Ação, Aventura",
            "Denis Villeneuve",
            "Timothée Chalamet, Zendaya, Rebecca Ferguson, Javier Bardem, Austin Butler",
            "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?auto=format&fit=crop&w=600&q=80",
            "https://www.youtube.com/embed/Way9Dexny3w",
            0,
            "em_cartaz"
        ),
        (
            6, 2,
            "O Fantasma da Ópera",
            "The Phantom of the Opera",
            "O mais aclamado musical de todos os tempos da Broadway chega aos palcos em uma montagem monumental. Nas catacumbas do lendário Teatro de Ópera de Paris, um misterioso gênio mascarado vive isolado e se apaixona perdidamente pela jovem soprano Christine Daaé.",
            "12",
            150,
            "Musical, Drama, Romance",
            "Harold Prince (Concepção)",
            "Companhia Brasileira de Teatro Lírico, 40 Músicos de Orquestra",
            "https://images.unsplash.com/photo-1460723237483-7a6dc9d0b212?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&w=600&q=80",
            "https://www.youtube.com/embed/fD36w1j0bYg",
            1,
            "em_cartaz"
        ),
        (
            7, 2,
            "O Auto da Compadecida",
            "O Auto da Compadecida",
            "Obra-prima inesquecível de Ariano Suassuna. As peripécias hilárias e sagazes de Chicó e João Grilo no sertão paraibano, enganando os poderosos até chegarem ao supremo julgamento celestial perante o Diabo, Jesus e a intervenção misericordiosa de Nossa Senhora.",
            "10",
            130,
            "Comédia, Drama, Folclore Brasileiro",
            "Guel Arraes (Inspiração Teatral)",
            "Elenco de Mestres do Teatro Nordestino e Trupe de Saltimbancos",
            "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=600&q=80",
            "https://www.youtube.com/embed/g6t5w2_2h44",
            1,
            "em_cartaz"
        )
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO eventos
        (id, categoria_id, titulo, titulo_original, sinopse, classificacao, duracao, genero, diretor, elenco, banner_url, poster_url, trailer_url, em_destaque, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        eventos
    )

    # 5. Sessões Programadas (Para Hoje, Amanhã e Dias Seguintes)
    hoje = datetime.now()
    d0 = hoje.strftime("%Y-%m-%d")
    d1 = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")
    d2 = (hoje + timedelta(days=2)).strftime("%Y-%m-%d")

    sessoes = [
        # O Jogo da Imitação (Sala 1 IMAX e Sala 2 VIP)
        (1, 1, 1, f"{d0} 16:30:00", "IMAX 2D", "LEG", 42.00, 1),
        (2, 1, 1, f"{d0} 19:45:00", "IMAX 2D", "LEG", 46.00, 1),
        (3, 1, 2, f"{d0} 21:00:00", "VIP 2D", "DUB", 52.00, 1),
        (4, 1, 1, f"{d1} 17:00:00", "IMAX 2D", "LEG", 44.00, 1),
        (5, 1, 2, f"{d1} 20:15:00", "VIP 2D", "LEG", 52.00, 1),

        # Oppenheimer (Sala 1 IMAX)
        (6, 2, 1, f"{d0} 14:00:00", "IMAX 2D", "LEG", 48.00, 1),
        (7, 2, 1, f"{d0} 21:30:00", "IMAX 2D", "LEG", 50.00, 1),
        (8, 2, 2, f"{d1} 16:00:00", "VIP 2D", "DUB", 54.00, 1),

        # Interestelar (Sala 1 IMAX e Sala 2 VIP)
        (9, 3, 1, f"{d0} 18:00:00", "IMAX 2D", "LEG", 44.00, 1),
        (10, 3, 2, f"{d1} 19:30:00", "VIP 2D", "LEG", 50.00, 1),

        # Divertida Mente 2 (Sala 2 VIP)
        (11, 4, 2, f"{d0} 14:30:00", "VIP 3D", "DUB", 46.00, 1),
        (12, 4, 2, f"{d0} 17:15:00", "VIP 3D", "DUB", 46.00, 1),
        (13, 4, 1, f"{d1} 14:15:00", "IMAX 3D", "DUB", 44.00, 1),

        # Duna: Parte 2 (Sala 1 IMAX)
        (14, 5, 1, f"{d2} 18:30:00", "IMAX 2D", "LEG", 46.00, 1),

        # Teatro: O Fantasma da Ópera (Sala 3 Teatro)
        (15, 6, 3, f"{d0} 20:00:00", "Palco Nobre", "NAC", 90.00, 1),
        (16, 6, 3, f"{d1} 19:00:00", "Palco Nobre", "NAC", 90.00, 1),

        # Teatro: O Auto da Compadecida (Sala 3 Teatro)
        (17, 7, 3, f"{d0} 16:00:00", "Palco Nobre", "NAC", 60.00, 1),
        (18, 7, 3, f"{d1} 21:30:00", "Palco Nobre", "NAC", 60.00, 1)
    ]

    # Agenda sem sobreposição na mesma sala, incluindo intervalo de limpeza.
    agenda = {
        1:(d0,'16:00'), 2:(d1,'16:00'), 3:(d0,'21:00'), 4:(d2,'16:00'),
        5:(d1,'21:00'), 6:(d0,'19:00'), 7:(d1,'19:00'), 8:(d2,'18:00'),
        9:(d0,'12:30'), 10:(d1,'17:30'), 11:(d0,'14:00'), 12:(d0,'17:15'),
        13:(d1,'12:30'), 14:(d2,'19:00'), 15:(d0,'20:00'), 16:(d1,'19:00'),
        17:(d0,'16:00'), 18:(d1,'15:30')
    }
    sessoes = [row[:3] + (f'{agenda[row[0]][0]} {agenda[row[0]][1]}:00',) + row[4:] for row in sessoes]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO sessoes
        (id, evento_id, sala_id, data_hora, formato, idioma, preco_base, ativa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sessoes
    )

    # 6. Produtos da Bomboniere
    produtos = [
        (
            1,
            "Combo Duplo CineSENAI",
            "1 Balde Gigante de Pipoca Salgada amanteigada + 2 Refrigerantes de 700ml à sua escolha.",
            "Combos",
            48.00,
            "https://images.unsplash.com/photo-1572177812156-58036aae439c?auto=format&fit=crop&w=500&q=80",
            1, 1
        ),
        (
            2,
            "Combo Mega Balde Colecionável",
            "1 Balde Balde Exclusivo de Alumínio colecionável + 1 Refrigerante de 1 Litro + 1 Chocolate M&Ms 150g.",
            "Combos",
            58.00,
            "https://images.unsplash.com/photo-1585647347483-22b66260dfff?auto=format&fit=crop&w=500&q=80",
            1, 1
        ),
        (
            3,
            "Combo Kids Pipoca & Suco",
            "1 Pipoca Média crocante + 1 Suco Del Valle 400ml + 1 Pacote de Balas Fini Tubes sortidas.",
            "Combos",
            34.00,
            "https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?auto=format&fit=crop&w=500&q=80",
            0, 1
        ),
        (
            4,
            "Pipoca Doce Gourmet Caramelizada",
            "Balde grande de pipoca especial artesanal coberta com calda de caramelo dourado crocante e flor de sal.",
            "Pipocas",
            30.00,
            "https://images.unsplash.com/photo-1512149673953-1e251807ec7c?auto=format&fit=crop&w=500&q=80",
            1, 1
        ),
        (
            5,
            "Pipoca Salgada Manteiga Imperial",
            "Balde clássico de pipoca crocante com manteiga clarificada especial de cinema e sal refinado.",
            "Pipocas",
            26.00,
            "https://images.unsplash.com/photo-1578849278619-e73505e9610f?auto=format&fit=crop&w=500&q=80",
            0, 1
        ),
        (
            6,
            "Nachos Crocantes com Queijo Cheddar",
            "Porção generosa de tortilhas de milho douradas servidas com generosa porção de creme cheddar quente.",
            "Pipocas",
            28.00,
            "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?auto=format&fit=crop&w=500&q=80",
            0, 1
        ),
        (
            7,
            "Coca-Cola Original 700ml",
            "Refrigerante gelado servido no copo temático oficial com gelo purificado.",
            "Bebidas",
            14.00,
            "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=500&q=80",
            0, 1
        ),
        (
            8,
            "Guaraná Antarctica 700ml",
            "Refrigerante clássico brasileiro sabor guaraná servido bem gelado.",
            "Bebidas",
            14.00,
            "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?auto=format&fit=crop&w=500&q=80",
            0, 1
        ),
        (
            9,
            "Água Mineral Crystal 500ml",
            "Água mineral natural sem gás, purificada e refrescante.",
            "Bebidas",
            8.00,
            "https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=500&q=80",
            0, 1
        ),
        (
            10,
            "M&M's Chocolate ao Leite 150g",
            "Pacote para compartilhar de deliciosas drágeas de chocolate crocantes e coloridas.",
            "Doces & Chocolates",
            15.00,
            "https://images.unsplash.com/photo-1582293041079-7814c2f12063?auto=format&fit=crop&w=500&q=80",
            0, 1
        ),
        (
            11,
            "Fini Tubes Morango Cítrico 80g",
            "Balas de gelatina ácidas em formato de tubo, sabor morango com açúcar cristal.",
            "Doces & Chocolates",
            10.00,
            "https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?auto=format&fit=crop&w=500&q=80",
            0, 1
        )
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO produtos_bomboniere
        (id, nome, descricao, categoria, preco, imagem_url, destaque, disponivel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        produtos
    )

    # 7. Clientes Exemplares
    clientes = [
        (1, "Carlos Eduardo Silva", "123.456.789-00", "carlos.silva@email.com", "(11) 98765-4321"),
        (2, "Mariana Oliveira Costa", "987.654.321-99", "mariana.costa@email.com", "(11) 97654-3210"),
        (3, "Lucas Santos Pereira", "456.789.123-44", "lucas.santos@email.com", "(11) 99123-4567")
    ]
    cursor.executemany(
        """
        INSERT OR IGNORE INTO clientes (id, nome, cpf, email, telefone)
        VALUES (?, ?, ?, ?, ?)
        """,
        clientes
    )

    # 8. Vendas e Ingressos Iniciais (para Sessão 2 de O Jogo da Imitação - mostrando assentos ocupados realistas!)
    # Vamos reservar os assentos D5, D6, D7 na sessão 2 para o cliente 1
    cursor.execute("SELECT id FROM assentos WHERE sala_id = 1 AND codigo = 'D5'")
    assento_d5 = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM assentos WHERE sala_id = 1 AND codigo = 'D6'")
    assento_d6 = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM assentos WHERE sala_id = 1 AND codigo = 'D7'")
    assento_d7 = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT OR IGNORE INTO vendas
        (id, cliente_id, sessao_id, codigo_localizador, data_venda, total_ingressos, total_bomboniere, total_geral, forma_pagamento, status)
        VALUES (1, 1, 2, 'CINE-84920', datetime('now', '-2 hours'), 92.00, 48.00, 140.00, 'PIX', 'APROVADO')
        """
    )

    # Ingressos da venda 1
    cursor.execute(
        """
        INSERT OR IGNORE INTO ingressos (venda_id, sessao_id, assento_id, tipo_ingresso, preco)
        VALUES
        (1, 2, ?, 'INTEIRA', 46.00),
        (1, 2, ?, 'MEIA', 23.00),
        (1, 2, ?, 'MEIA', 23.00)
        """,
        (assento_d5, assento_d6, assento_d7)
    )

    # Bomboniere da venda 1
    cursor.execute(
        """
        INSERT OR IGNORE INTO itens_venda_bomboniere (venda_id, produto_id, quantidade, preco_unitario, subtotal)
        VALUES (1, 1, 1, 48.00, 48.00)
        """
    )

    # Venda 2: Para o Fantasma da Ópera (Sessão 15)
    cursor.execute("SELECT id FROM assentos WHERE sala_id = 3 AND codigo = 'B7'")
    assento_b7 = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM assentos WHERE sala_id = 3 AND codigo = 'B8'")
    assento_b8 = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT OR IGNORE INTO vendas
        (id, cliente_id, sessao_id, codigo_localizador, data_venda, total_ingressos, total_bomboniere, total_geral, forma_pagamento, status)
        VALUES (2, 2, 15, 'TEATRO-31952', datetime('now', '-1 hour'), 135.00, 26.00, 161.00, 'CARTAO_CREDITO', 'APROVADO')
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO ingressos (venda_id, sessao_id, assento_id, tipo_ingresso, preco)
        VALUES
        (2, 15, ?, 'INTEIRA', 90.00),
        (2, 15, ?, 'MEIA', 45.00)
        """,
        (assento_b7, assento_b8)
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO itens_venda_bomboniere (venda_id, produto_id, quantidade, preco_unitario, subtotal)
        VALUES (2, 5, 1, 26.00, 26.00)
        """
    )

    print("Banco de dados inicializado e alimentado com sucesso!")

if __name__ == "__main__":
    init_db(force_recreate=True)
