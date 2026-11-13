"""Empacota apenas código, imagens e documentação e verifica uma instalação limpa."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'entrega'/'CineSENAI-projeto-completo.zip'
DEST.parent.mkdir(exist_ok=True)
files=[ROOT/name for name in ('app.py','README.md','requirements.txt','run.bat','.gitignore')]
for folder in ('database','templates','static','docs','tests','scripts'):
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file()
                 and '__pycache__' not in p.parts and p.suffix not in ('.db','.pyc')
                 and not p.name.startswith('cinema.db') and p.name != 'seed.sql')
with ZipFile(DEST,'w',ZIP_DEFLATED) as archive:
    for file in sorted(set(files)):
        archive.write(file,file.relative_to(ROOT).as_posix())

smoke = r'''
import re
from app import app
from database.db import get_db
client=app.test_client()
for route in ['/', '/evento/1','/evento/2','/evento/3','/evento/4','/evento/5','/evento/6','/evento/7','/?categoria=teatro','/bomboniere','/meus-ingressos','/informacoes','/admin','/projeto/','/projeto/DER.svg']:
    response=client.get(route)
    assert response.status_code == 200,(route,response.status_code)
    if response.mimetype=='text/html':
        for asset in re.findall(r'(?:src|href)="(/static/[^"?#]+)',response.text):
            assert client.get(asset).status_code==200,asset
conn=get_db()
assert conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not conn.execute('PRAGMA foreign_key_check').fetchall()
conflicts=conn.execute("""SELECT a.id,b.id FROM sessoes a JOIN sessoes b ON a.sala_id=b.sala_id AND a.id<b.id
    JOIN eventos ea ON ea.id=a.evento_id JOIN eventos eb ON eb.id=b.evento_id
    WHERE a.data_hora < datetime(b.data_hora, '+'||(eb.duracao+20)||' minutes')
    AND b.data_hora < datetime(a.data_hora, '+'||(ea.duracao+20)||' minutes')""").fetchall()
assert not conflicts,conflicts
print('Pacote limpo: 15 rotas OK; arquivos locais OK; banco integro; agenda sem sobreposicoes.')
print('Catalogo:',conn.execute('SELECT COUNT(*) FROM eventos').fetchone()[0],'eventos;',conn.execute('SELECT COUNT(*) FROM produtos_bomboniere').fetchone()[0],'produtos.')
conn.close()
'''
with tempfile.TemporaryDirectory(prefix='cinesenai-package-') as folder:
    with ZipFile(DEST) as archive:
        archive.extractall(folder)
    env=os.environ.copy()
    env.pop('CINESENAI_TESTING',None)
    env['CINESENAI_DB']=str(Path(folder)/'database'/'cinema.db')
    result=subprocess.run([sys.executable,'-X','utf8','-c',smoke],cwd=folder,env=env,capture_output=True,text=True,encoding='utf-8')
    print(result.stdout)
    if result.returncode:
        print(result.stderr)
        sys.exit(result.returncode)
print(f'Entregável: {DEST.name}; {len(set(files))} arquivos; {DEST.stat().st_size:,} bytes.')
