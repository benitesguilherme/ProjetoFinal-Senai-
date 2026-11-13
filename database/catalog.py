"""Atualização não destrutiva do catálogo acadêmico e agenda demonstrativa."""
from datetime import datetime, timedelta

def prepare_catalog(conn):
    films = {
        'O Jogo da Imitação': ('imitacao-poster.jpg', 'imitacao-banner.jpg'),
        'Oppenheimer': ('oppenheimer-poster.jpg', 'oppenheimer-poster.jpg'),
        'Interestelar': ('interestelar-poster.jpg', 'interestelar-banner.jpg'),
        'Divertida Mente 2': ('divertida-poster.jpg', 'divertida-poster.jpg'),
        'Duna: Parte 2': ('duna-poster.jpg', 'duna-poster.jpg'),
        'O Fantasma da Ópera': ('teatro.jpg', 'teatro.jpg'),
        'O Auto da Compadecida': ('teatro.jpg', 'teatro.jpg'),
    }
    for title, (poster, banner) in films.items():
        conn.execute('UPDATE eventos SET poster_url=?, banner_url=? WHERE titulo=?',
                     ('/static/images/'+poster, '/static/images/'+banner, title))
    conn.execute("UPDATE eventos SET diretor='Montagem demonstrativa', elenco='Elenco fictício para o projeto acadêmico', trailer_url='' WHERE categoria_id=2 AND id IN (6,7)")
    for pid in range(1,12):
        conn.execute('UPDATE produtos_bomboniere SET imagem_url=? WHERE id=?', (f'/static/images/produto-{pid}.svg',pid))
    # Não altera nem remove sessões antigas, ingressos ou vendas.
    slots = [(1,1,'16:00',42,'LEG'), (1,2,'21:00',52,'DUB'),
             (2,1,'19:00',48,'LEG'), (3,2,'17:30',46,'LEG'),
             (4,2,'14:00',40,'DUB'), (5,1,'12:30',46,'LEG'),
             (6,3,'20:00',90,'NAC'), (7,3,'16:00',60,'NAC')]
    for offset in range(7):
        day = (datetime.now() + timedelta(days=offset)).strftime('%Y-%m-%d')
        for event, room, time, price, language in slots:
            stamp = f'{day} {time}:00'
            # Respeita a programação já cadastrada, inclusive sobreposição de duração.
            clash = conn.execute('''SELECT 1 FROM sessoes s JOIN eventos e ON e.id=s.evento_id
                WHERE s.sala_id=? AND s.data_hora < datetime(?, '+' ||
                  (SELECT duracao+20 FROM eventos WHERE id=?) || ' minutes')
                AND datetime(s.data_hora, '+' || (e.duracao+20) || ' minutes') > ?''',
                (room, stamp, event, stamp)).fetchone()
            if not clash:
                conn.execute('''INSERT INTO sessoes(evento_id,sala_id,data_hora,formato,idioma,preco_base,ativa)
                    VALUES(?,?,?,?,?,?,1)''', (event,room,stamp,'Palco Nobre' if room==3 else 'VIP 2D' if room==2 else 'IMAX 2D',language,price))
    conn.commit()
