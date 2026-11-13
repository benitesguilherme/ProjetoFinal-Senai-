# Documentação técnica — CineSENAI

## 1. Problema e objetivo
Uma empresa de ingressos precisa organizar filmes e peças, salas, horários, poltronas e vendas. O CineSENAI atende a esse cenário em uma aplicação web local com banco relacional, catálogo, compra simulada e painel de gestão.

## 2. Tecnologias e justificativa
| Camada | Tecnologia | Justificativa |
| --- | --- | --- |
| Servidor | Python 3.11+ e Flask 3 | Rotas simples, validação de dados e fácil apresentação em laboratório. |
| Interface | HTML5, Jinja2, CSS e JavaScript | Renderização pelo servidor; interações sem exigir instalação de Node.js. |
| Dados | SQLite 3 | Banco relacional persistente em arquivo, com transações e chaves estrangeiras. |
| QR | qrcode e Pillow | Geração local do QR demonstrativo do voucher. |
| Verificação | unittest e cliente de teste Flask | Exercita rotas e regras em banco temporário independente. |

## 3. Arquitetura
Navegador → rotas Flask em app.py → consultas parametrizadas SQLite → templates Jinja2 → navegador.

O JavaScript controla seleção de poltronas, modalidade, quantidade de combos e atualização visual dos totais. A API recalcula os preços usando o banco. Um preço enviado pelo navegador não autoriza desconto.

Arquivos: app.py (rotas e regras), database/schema.sql (DDL), database/seed.py (dados iniciais), database/catalog.py (cartazes e agenda demonstrativa), templates/ (páginas), static/ (CSS, JS, imagens), tests/ (testes), docs/ (entrega).

## 4. Requisitos funcionais
| ID | Requisito | Implementação |
| --- | --- | --- |
| RF01 | Listar filmes e teatro | Catálogo com cartazes, categoria e pesquisa por título, gênero e diretor. |
| RF02 | Exibir ficha da obra | Sinopse, duração, classificação, direção, elenco e trailer de filmes. |
| RF03 | Escolher sessão | Datas, horários, sala, idioma, formato e preços. |
| RF04 | Escolher assentos | Mapa por fileira, espaços acessíveis, estados disponível/selecionado/ocupado. |
| RF05 | Inteira e meia | Modalidade individual por poltrona e meia de 50%. |
| RF06 | Adicionar produtos | Combos, pipocas, bebidas e doces; inclusão opcional. |
| RF07 | Simular pagamento | Pix, cartão ou pagamento pendente na bilheteria. |
| RF08 | Emitir voucher | Localizador, QR demonstrativo, resumo e impressão/PDF pelo navegador. |
| RF09 | Consultar ingresso | Localizador e e-mail levam ao voucher. |
| RF10 | Gerenciar catálogo | Cadastro e status de filmes/peças e cadastro, pausa e exclusão protegida de sessões. |
| RF11 | Acompanhar operação | Histórico de pedidos, totais e ocupação no painel local. |

## 5. Regras de negócio
- Cada pedido contém de 1 a 8 poltronas distintas de uma única sessão.
- A poltrona deve estar ativa e pertencer à sala da sessão.
- Sessão passada ou inativa não aceita compras.
- INTEIRA usa o preço da sessão; MEIA corresponde à metade.
- Cada produto deve estar disponível e ter quantidade inteira de 1 a 20; produtos duplicados são rejeitados.
- Preços de ingresso e produtos são buscados novamente no servidor.
- A compra usa BEGIN IMMEDIATE; venda, ingressos e produtos são gravados na mesma transação. Uma falha executa rollback.
- UNIQUE(sessao_id, assento_id) impede venda duplicada mesmo com requisições simultâneas.
- A interface consulta ocupação a cada 5 segundos. Selecionar no mapa não cria bloqueio temporário; a garantia acontece na confirmação.
- Pix e cartão geram APROVADO apenas no contexto simulado. BALCAO gera PENDENTE e ocupa as poltronas, sem expiração automática.
- O cadastro de sessões normaliza o datetime-local e verifica conflito na sala, incluindo 20 minutos de intervalo.
- Os novos localizadores usam 16 dígitos hexadecimais aleatórios. O QR não inclui CPF.

## 6. Rotas principais
| Método | Caminho | Finalidade |
| --- | --- | --- |
| GET | / | Catálogo e busca q/categoria. |
| GET | /evento/<id> | Ficha e sessões futuras. |
| GET | /sessao/<id>/assentos | Mapa e modalidades. |
| GET/POST | /sessao/<id>/bomboniere | Produtos e resumo. |
| GET/POST | /checkout | Revisão da compra. |
| POST | /api/finalizar-compra | Validação e transação da compra. |
| GET | /api/sessao/<id>/assentos | Ocupação em JSON. |
| GET | /confirmacao/<localizador> | Voucher. |
| GET/POST | /meus-ingressos | Consulta por localizador e e-mail. |
| GET | /bomboniere e /informacoes | Catálogo de produtos e ajuda. |
| GET | /admin | Painel acadêmico local. |

## 7. Persistência e inicialização
Na primeira execução, o banco é criado a partir do schema e do seed. Ao iniciar, o catálogo conhecido recebe imagens locais e sessões demonstrativas para os próximos sete dias. A rotina é idempotente e respeita horários já cadastrados; não apaga vendas nem muda os horários de pedidos antigos. A agenda é renovada na inicialização, não por serviço agendado.

Um banco existente que falha na leitura não é apagado automaticamente. CINESENAI_DB permite escolher outro arquivo; CINESENAI_SECRET define a chave de sessão; PORT altera a porta. O servidor padrão escuta apenas em 127.0.0.1, sem debugger.

## 8. Verificação
Execute `.venv\Scripts\python.exe -m unittest discover -s tests -v`. A suíte usa pasta temporária e não reseta o banco de demonstração. Cobre catálogo, busca, detalhes, mapa, combos, valores, modalidades, voucher, painel, lotação, dados inválidos, sessões passadas e concorrência real com duas threads. Veja RELATORIO_DE_TESTES.md para o resultado observado.

## 9. Limites do projeto acadêmico
Não há gateway, envio de e-mail, autenticação de clientes, autenticação do administrador, check-in real, cancelamento, reembolso, controle de estoque ou expiração de reserva. Não usar dados pessoais reais. O localizador funciona como acesso direto ao voucher; conhecer o link permite visualizá-lo. O formulário de consulta não substitui autenticação.

O CPF é validado por formato de 11 dígitos, sem cálculo dos dígitos verificadores para permitir a demonstração. Valores monetários usam REAL com os preços demonstrativos; uma versão comercial deveria migrar para centavos inteiros ou decimais exatos. O cadastro de obras não é um sistema completo de distribuição cinematográfica. O painel é destinado à execução local no laboratório e exige autenticação, proteção CSRF, autorização, revisão de privacidade e servidor WSGI antes de qualquer exposição pública.

## 10. Divisão de responsabilidades — proposta para revisão
Os nomes Benito e Sandro constavam nos documentos anteriores da pasta. A matriz abaixo é uma proposta de organização; deve ser ajustada pela equipe para refletir quem realmente realizou cada parte antes da entrega.

| Responsável sugerido | Parte | Evidência a apresentar |
| --- | --- | --- |
| Benito | Modelagem, SQLite, rotas e transações | Explicar DER, consultas e proteção contra venda duplicada. |
| Sandro | Interface, responsividade e interações | Demonstrar catálogo, mapa, combos e checkout. |
| Dupla | Requisitos, validação e apresentação | Executar testes, revisar manual e explicar decisões. |

O projeto recebeu auxílio de IA na implementação, pesquisa, revisão e documentação. Cada integrante deve compreender e revisar o material conforme as orientações do professor.
