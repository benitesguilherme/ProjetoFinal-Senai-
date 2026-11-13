# Relatório de verificação — 9 de novembro de 2026

## Testes automatizados
Resultado observado: **31 testes aprovados, 0 falhas**, em 2,128 segundos na última execução da suíte.
Comando: `.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v`.

- 14 testes da base: catálogo, filtros, ficha, mapa, API de assentos, bomboniere, compra, ocupação duplicada, voucher, administração, exclusões protegidas, pré-condições e sessão esgotada.
- 17 testes adicionais: poltrona de outra sala, assento repetido, modalidade inválida, limite por pedido, produto indisponível, quantidades inválidas, preços calculados no servidor, balcão pendente, cartão simulado, concorrência com duas threads, sessão passada, JSON inválido, checkout inválido, consulta de pedidos, busca vazia/páginas auxiliares, sobreposição administrativa e agenda inicial sem conflito.
- Banco de teste em diretório temporário. Nenhuma execução da suíte reseta database/cinema.db.

## Verificação pelo navegador
- Referências Cinemark e Cinépolis consultadas; homepage e organização da programação inspecionadas.
- Catálogo final com os cinco cartazes de cinema corretos e duas peças demonstrativas.
- Troca de data alterou as sessões visíveis.
- Seleção D5 e D6 na sessão de O Jogo da Imitação; uma inteira de R$ 42,00 e uma meia de R$ 21,00 resultaram em R$ 63,00.
- Combo Duplo de R$ 48,00 adicionado; checkout e voucher Pix simulado confirmaram R$ 111,00.
- Segunda compra no viewport móvel: D7 meia + combo, cartão de demonstração, total de R$ 69,00, voucher emitido.
- Reabertura do mapa confirmou D5, D6 e D7 ocupadas após persistência e reinicialização do servidor.
- Viewport móvel de 390 × 844: início, checkout, voucher e mapa conferidos. A largura do documento não ultrapassou a largura do viewport; o mapa tem rolagem própria.
- Caderno HTML e DER SVG renderizados e inspecionados.
- Capturas em docs/previews/.

## Limites da evidência
Validação em ambiente local, navegador desktop e viewport móvel emulado. Não constitui teste em celular físico, auditoria completa de acessibilidade ou homologação comercial. Pagamentos bancários, e-mails, publicação e check-in real não foram executados porque não integram esta versão.

## Dados preservados
As quatro vendas existentes antes do trabalho foram preservadas. Duas compras com dados fictícios foram acrescentadas durante a verificação visual. A cópia .backups/antes-redesign.zip contém o estado anterior. O ZIP de entrega exclui o banco em uso e recria somente os dados demonstrativos ao iniciar.

## Verificação do pacote de entrega
O ZIP foi extraído em uma pasta temporária. A inicialização criou um banco novo com 7 eventos e 11 produtos. As 15 rotas principais e seus recursos locais responderam com sucesso; o banco passou em integrity_check e foreign_key_check, e a agenda não apresentou sobreposições. O banco local de trabalho não foi incluído no arquivo.
