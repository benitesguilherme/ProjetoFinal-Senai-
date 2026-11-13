-- ====================================================================
-- CineSENAI & Teatro - Sistema de Gestão de Bilheteria e Bomboniere
-- Projeto Final de Curso SENAI
-- Autores: O Usuário e Sandro
-- Esquema do Banco de Dados Relacional (SQLite)
-- ====================================================================

PRAGMA foreign_keys = ON;

-- 1. Categorias de Entretenimento (Cinema, Teatro, Eventos Especiais)
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    icone TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    descricao TEXT
);

-- 2. Eventos / Obras em Cartaz (Filmes e Peças de Teatro)
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    titulo_original TEXT,
    sinopse TEXT NOT NULL,
    classificacao TEXT NOT NULL, -- 'Livre', '10', '12', '14', '16', '18'
    duracao INTEGER NOT NULL,    -- em minutos
    genero TEXT NOT NULL,
    diretor TEXT,
    elenco TEXT,
    banner_url TEXT NOT NULL,
    poster_url TEXT NOT NULL,
    trailer_url TEXT,
    em_destaque BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'em_cartaz', -- 'em_cartaz', 'em_breve', 'encerrado'
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
);

-- 3. Salas e Auditórios
CREATE TABLE IF NOT EXISTS salas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,      -- Ex: 'Sala 01 - IMAX Laser', 'Teatro Principal'
    tipo TEXT NOT NULL,             -- 'IMAX', 'VIP', 'Convencional', 'Teatro'
    capacidade INTEGER NOT NULL,
    total_fileiras INTEGER NOT NULL,
    assentos_por_fileira INTEGER NOT NULL
);

-- 4. Assentos das Salas
CREATE TABLE IF NOT EXISTS assentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    fileira TEXT NOT NULL,          -- 'A', 'B', 'C', ...
    numero INTEGER NOT NULL,       -- 1, 2, 3, ...
    codigo TEXT NOT NULL,           -- 'A1', 'A2', 'B1' ...
    tipo_assento TEXT DEFAULT 'PADRAO', -- 'PADRAO', 'VIP', 'CADEIRANTE', 'ACOMPANHANTE'
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE CASCADE,
    UNIQUE(sala_id, codigo)
);

-- 5. Sessões Programadas
CREATE TABLE IF NOT EXISTS sessoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id INTEGER NOT NULL,
    sala_id INTEGER NOT NULL,
    data_hora DATETIME NOT NULL,
    formato TEXT NOT NULL,          -- '2D', '3D', 'IMAX 3D', 'VIP 2D', 'Palco Tradicional'
    idioma TEXT NOT NULL,           -- 'DUB' (Dublado), 'LEG' (Legendado), 'NAC' (Nacional)
    preco_base REAL NOT NULL,       -- Preço da Inteira
    ativa BOOLEAN DEFAULT 1,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE RESTRICT
);

-- 6. Produtos da Bomboniere (Snack Bar)
CREATE TABLE IF NOT EXISTS produtos_bomboniere (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,        -- 'Combos', 'Pipocas', 'Bebidas', 'Doces & Chocolates'
    preco REAL NOT NULL,
    imagem_url TEXT NOT NULL,
    destaque BOOLEAN DEFAULT 0,
    disponivel BOOLEAN DEFAULT 1
);

-- 7. Clientes / Compradores
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL,
    email TEXT NOT NULL,
    telefone TEXT NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. Vendas / Pedidos
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    sessao_id INTEGER NOT NULL,
    codigo_localizador TEXT NOT NULL UNIQUE, -- Ex: 'CINE-84920'
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_ingressos REAL NOT NULL DEFAULT 0.0,
    total_bomboniere REAL NOT NULL DEFAULT 0.0,
    total_geral REAL NOT NULL,
    forma_pagamento TEXT NOT NULL,          -- 'PIX', 'CARTAO_CREDITO', 'BALCAO'
    status TEXT NOT NULL DEFAULT 'APROVADO', -- 'APROVADO', 'PENDENTE', 'CANCELADO'
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (sessao_id) REFERENCES sessoes(id) ON DELETE RESTRICT
);

-- 9. Ingressos Emitidos (Cadeiras Ocupadas por Sessão)
CREATE TABLE IF NOT EXISTS ingressos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    sessao_id INTEGER NOT NULL,
    assento_id INTEGER NOT NULL,
    tipo_ingresso TEXT NOT NULL,     -- 'INTEIRA' ou 'MEIA'
    preco REAL NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    FOREIGN KEY (sessao_id) REFERENCES sessoes(id) ON DELETE RESTRICT,
    FOREIGN KEY (assento_id) REFERENCES assentos(id) ON DELETE RESTRICT,
    UNIQUE(sessao_id, assento_id)   -- REGRA DE INTEGRIDADE: Impede venda dupla do mesmo assento na mesma sessão!
);

-- 10. Itens de Bomboniere Vendidos no Pedido
CREATE TABLE IF NOT EXISTS itens_venda_bomboniere (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos_bomboniere(id) ON DELETE RESTRICT
);

-- Índices para Otimização de Consultas Frequentes
CREATE INDEX IF NOT EXISTS idx_eventos_categoria ON eventos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_evento ON sessoes(evento_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_data ON sessoes(data_hora);
CREATE INDEX IF NOT EXISTS idx_ingressos_sessao ON ingressos(sessao_id);
CREATE INDEX IF NOT EXISTS idx_assentos_sala ON assentos(sala_id);
CREATE INDEX IF NOT EXISTS idx_vendas_localizador ON vendas(codigo_localizador);
