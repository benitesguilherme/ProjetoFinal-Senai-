# Roteiro de apresentação — 8 a 10 minutos

1. Problema (1 min): uma empresa precisa vender ingressos para cinema e teatro, evitar venda duplicada e organizar sessões.
2. Tecnologias (1 min): Python/Flask no servidor; SQLite para persistência; HTML/CSS/JS na interface. Explique por que o banco não é apenas uma lista em memória.
3. Demonstração (3 min): abra O Jogo da Imitação; selecione uma data futura; escolha duas poltronas; mude uma para meia; inclua um combo; use os dados fictícios; confirme e mostre o voucher.
4. Modelagem (2 min): abra DER.svg. Mostre evento → sessão → sala → assento; depois cliente → venda → ingressos e itens de bomboniere. Explique por que a ocupação depende de sessão + assento.
5. Confiabilidade (1 min): apresente a restrição UNIQUE e a transação. Mostre que os preços são recalculados no servidor e que dois clientes disputando uma cadeira resultam em uma compra e um conflito.
6. Gestão e limites (1 min): mostre o painel, diga que pagamento é simulado e que a aplicação é local. Diferencie demonstração acadêmica de operação comercial.
7. Responsabilidades (1 min): use a matriz revisada pela equipe, reconheça ferramentas de auxílio e explique o que cada integrante aprendeu e validou.

## Preparação
- Revise os nomes e a divisão de trabalho antes da entrega.
- Inicie o servidor e abra o site antes de começar a apresentação.
- Use sessão futura e poltronas ainda livres.
- Tenha o DER e o caderno HTML abertos; imprima como PDF se o professor solicitar.
- Não restaure o banco durante a apresentação. Os testes automatizados já usam outro banco.

## Perguntas que a equipe deve saber responder
- Qual diferença entre evento, sessão, sala e assento?
- Como uma mesma poltrona pode ser vendida para sessões diferentes?
- O que acontece se duas pessoas confirmarem o mesmo lugar?
- Por que o servidor recalcula o preço?
- O que é chave primária, estrangeira, transação, rollback e índice único?
- Quais partes seriam necessárias antes de operar comercialmente?
