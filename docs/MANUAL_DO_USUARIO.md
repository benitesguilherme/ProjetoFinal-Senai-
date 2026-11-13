# Manual de uso — CineSENAI

## 1. Iniciar
No Windows, abra run.bat na pasta do projeto. Aguarde o endereço http://127.0.0.1:5000 aparecer e abra-o no navegador. É necessário Python 3.11 ou mais recente. Na primeira preparação, instale as dependências com `python -m pip install -r requirements.txt`.

## 2. Encontrar uma história
Na página inicial, use Em cartaz, Cinema ou Teatro. A pesquisa aceita título, gênero ou diretor. O destaque abre O Jogo da Imitação. Cartazes levam à ficha com sinopse, duração e elenco. Filmes antigos fazem parte de uma mostra fictícia; não representam a programação real de cinemas.

## 3. Escolher a sessão
Na ficha, clique em uma data e escolha o horário. Confira sala, idioma, formato, inteira e meia. Datas sem sessões futuras deixam de aparecer. O trailer depende de internet.

## 4. Escolher poltronas e modalidade
Clique nas cadeiras desejadas (até oito). Clique novamente para retirar uma seleção. Cadeiras ocupadas não podem ser escolhidas. O mapa mostra a frente da sala ou do palco e os lugares de acessibilidade. No celular, deslize apenas a área do mapa para ver todas as cadeiras.

No resumo, escolha Inteira ou Meia-Entrada para cada lugar. O subtotal muda imediatamente. Avançar para Bomboniere só fica disponível com ao menos uma poltrona. A seleção não bloqueia o lugar para outros clientes; se houver conflito, o sistema pede outra escolha.

## 5. Adicionar pipoca e combos
Use + e − ao lado dos produtos. Os filtros separam combos, pipocas, bebidas e doces. Confira o total de ingressos mais produtos. Avançar para Pagamento leva os itens selecionados; Pular Bomboniere continua só com ingressos.

## 6. Testar o pagamento
Clique em Preencher dados fictícios para testar, ou preencha nome, CPF no formato de 11 números, telefone e e-mail fictícios. Escolha Pix, Cartão de Crédito ou Bilheteria/Balcão.

O Pix mostra um QR ilustrativo sem valor bancário. O cartão tem campos demonstrativos e os dados bancários não são enviados ao servidor. Bilheteria/Balcão gera pedido pendente. A confirmação não faz cobrança real. O botão de dados fictícios também preenche um cartão de demonstração.

## 7. Guardar o ingresso
Após confirmar, a página mostra localizador, sessão, poltronas, modalidades e combos. Use Imprimir / Salvar Ingresso (PDF) para abrir a impressão do navegador e escolher Salvar como PDF. O voucher não tem validade comercial.

## 8. Reencontrar o pedido
Clique em Meus ingressos. Digite o localizador completo (CINE-... ou TEATRO-...) e o e-mail usado. O sistema não envia e-mail: copie o código na confirmação.

## 9. Área de gestão
No rodapé, abra Área de gestão. Consulte vendas, ocupação, obras e sessões. É possível cadastrar obras, mudar status, cadastrar horários e pausar sessões. Sessões com ingressos são preservadas no histórico quando se solicita exclusão. A restauração de demonstração apaga o histórico: use somente em uma cópia descartável e faça backup antes.

## 10. Problemas comuns
| Situação | Como resolver |
| --- | --- |
| Página não abre | Mantenha o terminal do servidor aberto e confira a porta 5000. |
| Poltrona ocupada durante a compra | Volte ao mapa e escolha outro lugar. |
| Nenhuma sessão aparece | Reinicie o servidor para renovar a agenda, ou cadastre uma sessão futura na gestão. |
| Pedido não encontrado | Confira localizador e e-mail; não há envio automático por e-mail. |
| Imagem ou trailer externo indisponível | Cartazes principais são locais; trailer, fontes e alguns recursos dependem de internet. |
| Erro ao abrir banco | Preserve o arquivo cinema.db e verifique o erro no terminal; não apague o banco para corrigir. |
