# CineSENAI — Cinema & Teatro

Sistema acadêmico de venda de ingressos, com Python, Flask e SQLite. Catálogo de filmes e peças, sinopses, sessões, mapa de poltronas, inteira/meia, combos, checkout simulado, voucher, consulta de pedidos e painel local de gestão.

## Executar no Windows
Abra `run.bat` e acesse http://127.0.0.1:5000.

Ou execute:
```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

O banco é criado automaticamente quando não existe. A agenda demonstrativa é renovada ao iniciar, preservando vendas e sessões existentes. O servidor fica disponível apenas neste computador por padrão. Use Python 3.11+.

## Entrega acadêmica
- [Caderno completo imprimível](docs/ENTREGA.html)
- [Documentação técnica](docs/DOCUMENTACAO_TECNICA.md)
- [Manual do usuário](docs/MANUAL_DO_USUARIO.md)
- [DER vetorial](docs/DER.svg) e [modelagem](docs/DER.md)
- [Pesquisa e referências](docs/REFERENCIAS_DESIGN.md)
- [Roteiro de apresentação](docs/ROTEIRO_APRESENTACAO.md)
- [Relatório de testes](docs/RELATORIO_DE_TESTES.md)

## Testar
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
Os testes usam banco temporário; não apagam vendas do projeto.

## Demonstração
Escolha um filme, data e lugares. Defina inteira/meia por poltrona, adicione um combo e avance. No checkout, use **Preencher dados fictícios para testar**. Pix e cartão não fazem cobrança; bilheteria gera pedido pendente. Guarde o localizador para consultar em Meus ingressos. O voucher pode ser impresso ou salvo em PDF pelo navegador.

## Limites
É uma aplicação de demonstração local, sem autenticação administrativa, pagamentos bancários, envio de e-mail, check-in, cancelamento ou expiração de reservas. Não publicar diretamente nem usar dados reais. Veja a documentação para detalhes. Os nomes e a divisão de responsabilidades encontrados nos documentos anteriores foram mantidos como proposta a revisar pela equipe.

O arquivo .backups/antes-redesign.zip preserva o estado anterior à revisão. Ele contém o banco anterior; não faz parte do pacote para entrega.
