"""Gera a documentação acadêmica em Markdown, HTML imprimível e DER vetorial."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'docs'
DOCS.mkdir(exist_ok=True)

technical = '''# Documentação técnica — CineSENAI

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
Execute `.venv\\Scripts\\python.exe -m unittest discover -s tests -v`. A suíte usa pasta temporária e não reseta o banco de demonstração. Cobre catálogo, busca, detalhes, mapa, combos, valores, modalidades, voucher, painel, lotação, dados inválidos, sessões passadas e concorrência real com duas threads. Veja RELATORIO_DE_TESTES.md para o resultado observado.

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
'''

manual = '''# Manual de uso — CineSENAI

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
'''

references = '''# Pesquisa e direção de design

Pesquisa realizada em 9 de novembro de 2026. Referências examinadas por conteúdo e, para Cinemark e Cinépolis, também pelo navegador. Não houve compra nos sites pesquisados nem inspeção de checkout autenticado.

| Referência | Padrão observado | Decisão aplicada |
| --- | --- | --- |
| [Cinemark](https://www.cinemark.com.br/) | Imagens cinematográficas grandes, cartazes, separação de filmes e snack bar. | Hero com imagem do filme, cartazes reconhecíveis, entrada própria para bomboniere. |
| [Cinépolis](https://www.cinepolis.com.br/) | Abas de programação e uma sequência de datas para sessões. | Datas selecionáveis e sessões agrupadas por dia. |
| [CineCanon — The Imitation Game](https://www.cinecanon.com/films/the-imitation-game-2014) | Referência de filme, direção e imagem do catálogo TMDB. | Conferência do banner de O Jogo da Imitação; texto da interface redigido para o projeto. |

## Identidade própria
Fundo carvão #111112, vermelho #e83b45 e texto branco suave. Barlow Condensed no título do destaque e DM Sans no restante. A fotografia e os cartazes são protagonistas; bordas, sombras e movimentos são discretos. Layout com cinco cartazes por linha no desktop e dois no celular. Teatro recebe tratamento tipográfico próprio; bomboniere aparece em uma composição quente e independente.

## Fluxo adotado
Catálogo → ficha/sessão → poltrona e modalidade → combo opcional → dados e pagamento simulado → voucher. O resumo acompanha as etapas e os preços são recalculados pelo servidor. A navegação não exige cadastro para a demonstração.

## Materiais e atribuição
Cartazes de O Jogo da Imitação, Oppenheimer, Interestelar, Divertida Mente 2 e Duna: Parte 2 são materiais promocionais de seus titulares, obtidos pelo CDN do TMDB. O banner principal foi identificado na referência CineCanon e conferido visualmente. As URLs estão em static/images/sources.json. As imagens de pipoca e teatro vieram do Unsplash. Materiais são usados no contexto acadêmico; isso não declara licença de exploração comercial. Produtos ilustrados em SVG são desenhos do projeto. Fontes: Google Fonts; ícones: Font Awesome.

As referências orientam a organização, sem reproduzir a marca ou a interface integral das redes pesquisadas. Nomes de formatos de sala no banco são demonstrativos e não representam certificação.
'''

readme = '''# CineSENAI — Cinema & Teatro

Sistema acadêmico de venda de ingressos, com Python, Flask e SQLite. Catálogo de filmes e peças, sinopses, sessões, mapa de poltronas, inteira/meia, combos, checkout simulado, voucher, consulta de pedidos e painel local de gestão.

## Executar no Windows
Abra `run.bat` e acesse http://127.0.0.1:5000.

Ou execute:
```powershell
python -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.venv\\Scripts\\python.exe app.py
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
.venv\\Scripts\\python.exe -m unittest discover -s tests -v
```
Os testes usam banco temporário; não apagam vendas do projeto.

## Demonstração
Escolha um filme, data e lugares. Defina inteira/meia por poltrona, adicione um combo e avance. No checkout, use **Preencher dados fictícios para testar**. Pix e cartão não fazem cobrança; bilheteria gera pedido pendente. Guarde o localizador para consultar em Meus ingressos. O voucher pode ser impresso ou salvo em PDF pelo navegador.

## Limites
É uma aplicação de demonstração local, sem autenticação administrativa, pagamentos bancários, envio de e-mail, check-in, cancelamento ou expiração de reservas. Não publicar diretamente nem usar dados reais. Veja a documentação para detalhes. Os nomes e a divisão de responsabilidades encontrados nos documentos anteriores foram mantidos como proposta a revisar pela equipe.

O arquivo .backups/antes-redesign.zip preserva o estado anterior à revisão. Ele contém o banco anterior; não faz parte do pacote para entrega.
'''

presentation = '''# Roteiro de apresentação — 8 a 10 minutos

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
'''

der = '''# Diagrama Entidade-Relacionamento

O banco SQLite possui dez tabelas de domínio. Abra [DER.svg](DER.svg) para visualizar ou imprimir o desenho. A definição física completa está em database/schema.sql.

```mermaid
erDiagram
    CATEGORIAS ||--o{ EVENTOS : classifica
    EVENTOS ||--o{ SESSOES : programa
    SALAS ||--o{ SESSOES : recebe
    SALAS ||--o{ ASSENTOS : possui
    CLIENTES ||--o{ VENDAS : realiza
    SESSOES ||--o{ VENDAS : pertence
    VENDAS ||--|{ INGRESSOS : contem
    SESSOES ||--o{ INGRESSOS : aloca
    ASSENTOS ||--o{ INGRESSOS : identifica
    VENDAS ||--o{ ITENS_VENDA_BOMBONIERE : inclui
    PRODUTOS_BOMBONIERE ||--o{ ITENS_VENDA_BOMBONIERE : compoe
```

## Dicionário resumido
| Tabela | Chave primária | Chaves estrangeiras | Dados principais |
| --- | --- | --- | --- |
| categorias | id | — | nome e slug únicos, ícone e descrição. |
| eventos | id | categoria_id | título, sinopse, duração, gênero, classificação, imagens, status. |
| salas | id | — | nome único, tipo, capacidade, quantidade de fileiras e assentos. |
| assentos | id | sala_id | fileira, número, código, tipo e ativo; UNIQUE(sala_id,codigo). |
| sessoes | id | evento_id, sala_id | data_hora, formato, idioma, preco_base, ativa. |
| clientes | id | — | nome, CPF, e-mail e telefone; CPF não tem índice UNIQUE no schema atual. |
| vendas | id | cliente_id, sessao_id | localizador único, data, totais, forma_pagamento, status. |
| ingressos | id | venda_id, sessao_id, assento_id | tipo_ingresso, preço; UNIQUE(sessao_id,assento_id). |
| produtos_bomboniere | id | — | nome, categoria, preço, descrição, imagem, disponibilidade. |
| itens_venda_bomboniere | id | venda_id, produto_id | quantidade, preço unitário e subtotal. |

## Integridade e decisões
Uma venda pertence a um cliente e a uma sessão. A aplicação exige ao menos um ingresso por venda; a cardinalidade mínima não é imposta por uma constraint SQL. Uma poltrona pode aparecer em muitos ingressos ao longo do tempo, mas apenas uma vez na mesma sessão.

PRAGMA foreign_keys = ON é ativado em cada conexão. As referências são protegidas por chaves estrangeiras. A validação de assento/sala/sessão e dos tipos é responsabilidade da aplicação; o schema não possui todos os CHECKs de negócio. Não se deve contornar a API e inserir dados arbitrários diretamente no banco.

Os preços e totais são snapshots do pedido, preservados para histórico; são uma desnormalização deliberada. A combinação de UNIQUE e BEGIN IMMEDIATE protege a ocupação concorrente. Índices aceleram buscas por categoria, evento, data, sala e sessão. Não há tabela de pagamento bancário porque não existe integração com gateway.
'''

for filename, content in {'DOCUMENTACAO_TECNICA.md':technical,'MANUAL_DO_USUARIO.md':manual,'REFERENCIAS_DESIGN.md':references,'ROTEIRO_APRESENTACAO.md':presentation,'DER.md':der}.items():
    (DOCS/filename).write_text(content,encoding='utf-8')
(ROOT/'README.md').write_text(readme,encoding='utf-8')

# DER em SVG: componentes e ligações em camadas, sem dependência de renderizador externo.
tables = {
 'CATEGORIAS':(30,110,['PK id','nome · slug (únicos)','icone · descricao']),
 'EVENTOS':(355,110,['PK id · FK categoria_id','titulo · sinopse · duracao','genero · classificacao','diretor · elenco · imagens','status · em_destaque']),
 'SALAS':(1010,110,['PK id','nome (único) · tipo','capacidade · total_fileiras','assentos_por_fileira']),
 'SESSOES':(680,370,['PK id','FK evento_id · FK sala_id','data_hora · formato · idioma','preco_base · ativa']),
 'ASSENTOS':(1010,370,['PK id · FK sala_id','fileira · numero · codigo','tipo_assento · ativo','UK sala_id + codigo']),
 'CLIENTES':(30,625,['PK id','nome · cpf','email · telefone']),
 'VENDAS':(355,625,['PK id','FK cliente_id · FK sessao_id','codigo_localizador (único)','data · totais · forma_pagamento','status']),
 'INGRESSOS':(1010,625,['PK id · FK venda_id','FK sessao_id · FK assento_id','tipo_ingresso · preco','UK sessao_id + assento_id']),
 'PRODUTOS_BOMBONIERE':(30,910,['PK id','nome · descricao · categoria','preco · imagem · disponivel']),
 'ITENS_VENDA_BOMBONIERE':(680,910,['PK id · FK venda_id','FK produto_id','quantidade · preco_unitario','subtotal']),
}
edges=[('M305 160H355','1:N',322,150),('M490 290V330H815V370','1:N',642,319),('M1010 230H975V425H955','1:N',978,318)]
# Substitui o caminho horizontal da relação sala/sessão por uma curva simples.
edges[2]=('M1010 230H975V425H955','1:N',978,318)
edges += [('M1145 290V370','1:N',1155,335),('M305 690H355','1:N',321,680),('M680 490H650V605H490V625','1:N',582,596),('M630 710H1010','1:N',800,700),('M820 550V585H1010V655','1:N',897,577),('M1145 550V625','1:N',1155,590),('M490 805V865H815V910','1:N',647,855),('M305 980H680','1:N',485,969)]
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 1160" role="img" aria-label="Diagrama de entidades e relacionamentos do CineSENAI"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#a63743"/></marker></defs><rect width="1320" height="1160" fill="#faf9f7"/><text x="30" y="45" font-family="Arial" font-size="28" font-weight="bold" fill="#211d23">CineSENAI — Diagrama Entidade-Relacionamento</text><text x="30" y="76" font-family="Arial" font-size="14" fill="#625b66">PK: chave primária · FK: chave estrangeira · UK: unicidade · 1:N: um para muitos</text>']
for path,label,x,y in edges:
    svg.append(f'<path d="{path}" fill="none" stroke="#a63743" stroke-width="2" marker-end="url(#arrow)"/><text x="{x}" y="{y}" font-family="Arial" font-size="13" fill="#a63743">{label}</text>')
for name,(x,y,fields) in tables.items():
    svg.append(f'<g transform="translate({x},{y})"><rect width="275" height="180" rx="8" fill="white" stroke="#d5cdd3"/><path d="M8 0H267Q275 0 275 8V37H0V8Q0 0 8 0" fill="#29232a"/><text x="13" y="24" font-family="Arial" font-size="13" font-weight="bold" fill="white">{name}</text>')
    for i,field in enumerate(fields):svg.append(f'<text x="13" y="{61+i*23}" font-family="Arial" font-size="13" fill="#48414c">{escape(field)}</text>')
    svg.append('</g>')
svg.append('<text x="30" y="1135" font-family="Arial" font-size="13" fill="#625b66">A API valida sala/assento e a quantidade mínima. O banco garante as chaves e a unicidade da ocupação.</text></svg>')
(DOCS/'DER.svg').write_text(''.join(svg),encoding='utf-8')

def render_markdown(source):
    import re
    out=[];code=False;table=False
    for line in source.splitlines():
        if line.startswith('```'):
            if table:out.append('</tbody></table>');table=False
            out.append('</code></pre>' if code else '<pre><code>');code=not code;continue
        if code:out.append(escape(line)+'\n');continue
        if line.startswith('|'):
            if not table:out.append('<table><tbody>');table=True
            if re.match(r'^\|[\s:|\-]+$',line):continue
            out.append('<tr>'+''.join('<td>'+escape(c.strip())+'</td>' for c in line.strip('|').split('|'))+'</tr>');continue
        if table:out.append('</tbody></table>');table=False
        text=escape(line)
        text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
        text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',text)
        if line.startswith('### '):out.append('<h3>'+text[4:]+'</h3>')
        elif line.startswith('## '):out.append('<h2>'+text[3:]+'</h2>')
        elif line.startswith('# '):out.append('<h1>'+text[2:]+'</h1>')
        elif line.startswith('- '):out.append('<p class="bullet">• '+text[2:]+'</p>')
        elif line:out.append('<p>'+text+'</p>')
    if table:out.append('</tbody></table>')
    return '\n'.join(out)

parts=[technical,manual,der,references,presentation]
html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CineSENAI — Caderno do projeto</title><style>*{box-sizing:border-box}body{margin:0;background:#eeebe8;color:#29232a;font:15px/1.65 Arial,sans-serif}main{max-width:1050px;margin:35px auto;background:white;padding:65px}h1{font-size:34px;line-height:1.2;color:#9f2c38;letter-spacing:-1px}h2{font-size:21px;margin-top:32px}h3{font-size:17px}table{border-collapse:collapse;width:100%;font-size:12px;margin:20px 0}td{border:1px solid #ded8dc;padding:9px;vertical-align:top}tr:first-child{background:#f3eef0;font-weight:bold}a{color:#9f2c38}code{font-size:12px;overflow-wrap:anywhere}pre{white-space:pre-wrap;background:#f6f3f4;padding:18px}section{padding-bottom:35px;margin-bottom:45px;border-bottom:2px solid #ded8dc}.cover{background:#171419;color:white;padding:45px}.cover h1{color:white;font-size:55px}.cover p{color:#d0bfc7}.cover small{color:#f08893;letter-spacing:3px}.print{padding:12px 20px;border:0;background:#a82b3b;color:white;border-radius:5px;cursor:pointer}img{width:100%;height:auto}.bullet{margin:7px 0}nav{display:flex;gap:15px;flex-wrap:wrap;margin:30px 0;font-size:12px}@media(max-width:700px){main{padding:25px;margin:0}table{display:block;overflow:auto}.cover{padding:25px}.cover h1{font-size:36px}}@media print{body{background:white}main{margin:0;padding:0;max-width:none}.no-print,nav{display:none}.cover{break-after:page;background:white;color:#222}.cover h1{color:#9f2c38}.cover p{color:#555}section{break-before:page;border:0}h1,h2,h3{break-after:avoid}tr{break-inside:avoid}a{color:inherit;text-decoration:none}p{orphans:3;widows:3}}@page{size:A4;margin:18mm}</style><main><header class="cover"><small>PROJETO FINAL · SENAI</small><h1>Boas histórias.<br>Um sistema completo.</h1><p>CineSENAI — Bilheteria de cinema e teatro</p><p>Documentação técnica · Manual · Modelagem · Pesquisa</p><p>Python · Flask · SQLite · HTML/CSS/JavaScript</p><p>9 de novembro de 2026</p></header><nav><a href="#tecnica">Documentação técnica</a><a href="#manual">Manual</a><a href="#der">DER</a><a href="#referencias">Referências</a><a href="#apresentacao">Apresentação</a></nav><button class="print no-print" onclick="window.print()">Imprimir / Salvar como PDF</button>'''
for ident,part in zip(['tecnica','manual','der','referencias','apresentacao'],parts):
    html+=f'<section id="{ident}">'+render_markdown(part)
    if ident=='der':html+='<h2>Diagrama visual</h2><img src="DER.svg" alt="DER das dez tabelas do CineSENAI">'
    html+='</section>'
html+='</main></html>'
(DOCS/'ENTREGA.html').write_text(html,encoding='utf-8')
print('Documentação e DER gerados em docs/.')
