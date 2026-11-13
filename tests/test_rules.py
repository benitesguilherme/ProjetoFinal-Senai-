"""Regras financeiras, entradas inválidas e concorrência real em banco isolado."""
import copy
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from test_app import app, get_db, init_db

class PurchaseRulesTest(unittest.TestCase):
    def setUp(self):
        init_db(force_recreate=True)
        conn = get_db()
        conn.execute("UPDATE sessoes SET data_hora=?", ((datetime.now()+timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),))
        conn.commit()
        conn.close()
        self.client = app.test_client()
        self.payload = dict(sessao_id=1,nome='Cliente Demonstracao',cpf='12345678900',email='demo@example.com',telefone='11999999999',forma_pagamento='PIX',assentos=[dict(assento_id=28,tipo_ingresso='INTEIRA')],bomboniere=[])

    def post(self, payload=None):
        return self.client.post('/api/finalizar-compra', json=payload or self.payload)

    def test_assento_de_outra_sala_nao_cria_venda(self):
        self.payload['assentos'][0]['assento_id'] = 100
        conn=get_db(); before=conn.execute('SELECT COUNT(*) FROM vendas').fetchone()[0];conn.close()
        self.assertEqual(self.post().status_code,400)
        conn=get_db();self.assertEqual(conn.execute('SELECT COUNT(*) FROM vendas').fetchone()[0],before);conn.close()

    def test_assento_repetido(self):
        self.payload['assentos'] *= 2
        self.assertEqual(self.post().status_code,400)

    def test_tipo_invalido_nao_concede_meia(self):
        self.payload['assentos'][0]['tipo_ingresso']='GRATIS'
        self.assertEqual(self.post().status_code,400)

    def test_limite_oito_assentos(self):
        self.payload['assentos']=[dict(assento_id=i,tipo_ingresso='INTEIRA') for i in range(1,10)]
        self.assertEqual(self.post().status_code,400)

    def test_produto_indisponivel(self):
        conn=get_db();conn.execute('UPDATE produtos_bomboniere SET disponivel=0 WHERE id=1');conn.commit();conn.close()
        self.payload['bomboniere']=[dict(produto_id=1,quantidade=1)]
        self.assertEqual(self.post().status_code,400)

    def test_quantidades_invalidas(self):
        for qty in (-1,0,21,1.5,True,'abc'):
            with self.subTest(qty=qty):
                self.payload['bomboniere']=[dict(produto_id=1,quantidade=qty)]
                self.assertEqual(self.post().status_code,400)

    def test_recalculo_meia_combo_no_servidor(self):
        self.payload['assentos'] += [dict(assento_id=29,tipo_ingresso='MEIA',preco=0)]
        self.payload['bomboniere']=[dict(produto_id=1,quantidade=2,preco=0)]
        self.payload['total_geral']=0
        r=self.post();self.assertEqual(r.status_code,200)
        conn=get_db();row=conn.execute('SELECT total_ingressos,total_bomboniere,total_geral FROM vendas WHERE codigo_localizador=?',(r.json['codigo_localizador'],)).fetchone();conn.close()
        self.assertEqual(tuple(row),(63.0,96.0,159.0))

    def test_balcao_pendente(self):
        self.payload['forma_pagamento']='BALCAO'
        r=self.post();self.assertEqual(r.status_code,200)
        conn=get_db();row=conn.execute('SELECT status FROM vendas WHERE codigo_localizador=?',(r.json['codigo_localizador'],)).fetchone();conn.close()
        self.assertEqual(row['status'],'PENDENTE')
        self.assertIn('aguardando pagamento',self.client.get(r.json['redirect_url']).text)

    def test_cartao_simulado_sem_dados_bancarios(self):
        self.payload['forma_pagamento']='CARTAO_CREDITO'
        self.assertEqual(self.post().status_code,200)

    def test_duas_compras_concorrentes_mesmo_assento(self):
        def buy(i):
            payload=copy.deepcopy(self.payload);payload['cpf']=f'1234567890{i}'
            with app.test_client() as client:
                return client.post('/api/finalizar-compra',json=payload).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            codes=list(pool.map(buy,[1,2]))
        self.assertEqual(sorted(codes),[200,409])

    def test_sessao_passada(self):
        conn=get_db();conn.execute("UPDATE sessoes SET data_hora='2020-01-01 10:00:00' WHERE id=1");conn.commit();conn.close()
        self.assertEqual(self.post().status_code,404)
        self.assertEqual(self.client.get('/sessao/1/assentos').status_code,404)

    def test_corpo_json_invalido(self):
        for data in ([1],{'nome':123},dict(self.payload,assentos=[None]),dict(self.payload,bomboniere=[None])):
            with self.subTest(data=data):
                self.assertEqual(self.client.post('/api/finalizar-compra',json=data).status_code,400)

    def test_checkout_ids_invalidos(self):
        self.assertEqual(self.client.get('/checkout?sessao_id=1&assentos_ids=abc').status_code,400)
        self.assertEqual(self.client.get('/checkout?sessao_id=1&assentos_ids=100').status_code,400)

    def test_consulta_localizador_email(self):
        r=self.post();code=r.json['codigo_localizador']
        valid=self.client.post('/meus-ingressos',data=dict(codigo=code,email='demo@example.com'))
        self.assertEqual(valid.status_code,302)
        self.assertIn(code,valid.location)
        invalid=self.client.post('/meus-ingressos',data=dict(codigo=code,email='outro@example.com'))
        self.assertEqual(invalid.status_code,200)
        self.assertIn('Não encontramos',invalid.text)

    def test_busca_sem_resultados_e_paginas_auxiliares(self):
        self.assertIn('Nenhum título',self.client.get('/?q=zzzzsemfilme').text)
        for url in ['/bomboniere','/informacoes','/meus-ingressos']:
            self.assertEqual(self.client.get(url).status_code,200)

    def test_admin_impede_sobreposicao(self):
        conn=get_db();stamp=conn.execute('SELECT data_hora FROM sessoes WHERE id=1').fetchone()[0];before=conn.execute('SELECT COUNT(*) FROM sessoes').fetchone()[0];conn.close()
        response=self.client.post('/admin/sessao/nova',data=dict(evento_id=1,sala_id=1,data_hora=stamp,formato='2D',idioma='LEG',preco_base='42'),follow_redirects=True)
        self.assertIn('já tem uma sessão',response.text)
        conn=get_db();self.assertEqual(conn.execute('SELECT COUNT(*) FROM sessoes').fetchone()[0],before);conn.close()

    def test_seed_sem_sessoes_sobrepostas(self):
        init_db(force_recreate=True)
        conn=get_db()
        conflicts=conn.execute('''SELECT a.id,b.id FROM sessoes a
            JOIN sessoes b ON a.sala_id=b.sala_id AND a.id<b.id
            JOIN eventos ea ON ea.id=a.evento_id JOIN eventos eb ON eb.id=b.evento_id
            WHERE a.data_hora < datetime(b.data_hora, '+'||(eb.duracao+20)||' minutes')
            AND b.data_hora < datetime(a.data_hora, '+'||(ea.duracao+20)||' minutes')''').fetchall()
        conn.close()
        self.assertEqual(conflicts,[])
