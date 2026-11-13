"""Ilustrações vetoriais próprias para os produtos da bomboniere."""
from pathlib import Path
import random
ROOT=Path(__file__).resolve().parents[1]/'static'/'images'
random.seed(7)

def cup(x=350,y=145,scale=1,color='#d54247'):
    return f'<g transform="translate({x},{y}) scale({scale})"><path d="M58 5L72 -58" stroke="#eee3c7" stroke-width="9"/><path d="M0 0H110L94 175H16Z" fill="{color}"/><path d="M9 8H30L41 167H24Z" fill="#fff" opacity=".12"/><ellipse cx="55" cy="0" rx="59" ry="12" fill="#f5e8d6"/><ellipse cx="55" cy="-3" rx="51" ry="7" fill="#d4c6b4"/><text x="55" y="91" fill="#fff" font-family="Arial" font-size="18" font-weight="bold" text-anchor="middle">CINE</text><text x="55" y="111" fill="#fff" font-family="Arial" font-size="12" text-anchor="middle">SENAI</text></g>'

def popcorn(x=150,y=143,scale=1,color='#ca3d43'):
    kernels=''
    for _ in range(95):
        px=random.uniform(-5,172);py=random.uniform(-42,22)
        if ((px-83)/100)**2+((py+2)/50)**2>1:continue
        r=random.uniform(6,13)
        kernels+=f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{random.choice(["#fff0b7","#f5dc97","#fff8da","#e6c47c"])}" stroke="#d8b975" stroke-width="1"/>'
    return f'<g transform="translate({x},{y}) scale({scale})">{kernels}<path d="M0 14H170L146 185H25Z" fill="{color}"/><path d="M12 20H36L50 179H31ZM66 20H91L89 179H70ZM123 20H150L134 179H111Z" fill="#f9e7cf"/><ellipse cx="85" cy="14" rx="87" ry="13" fill="#fff0c1"/>{kernels}<circle cx="84" cy="103" r="39" fill="{color}"/><text x="84" y="100" text-anchor="middle" font-family="Arial" font-weight="bold" font-size="20" fill="#fff5e5">CINE</text><text x="84" y="118" text-anchor="middle" font-family="Arial" font-size="13" fill="#fff5e5">SENAI</text></g>'

for pid in range(1,12):
    drawing=''
    if pid<=5:
        drawing=popcorn(160 if pid in (4,5) else 125,130,1.1,'#be833b' if pid in (2,4) else '#ce454c')
        if pid in (1,2,3):drawing+=cup(345,160,.86,'#e74750' if pid!=3 else '#6497a3')
        if pid==1:drawing=cup(70,185,.72,'#942c36')+drawing
    elif pid in (7,8):drawing=cup(220,130,1.13,'#cb3644' if pid==7 else '#43826b')
    elif pid==9:
        drawing='<g transform="translate(220,65)"><rect x="25" y="0" width="62" height="27" rx="5" fill="#8bbbc7"/><path d="M30 27H82V57Q110 80 110 105V240Q110 260 92 260H20Q2 260 2 240V105Q2 80 30 57Z" fill="#9acbd5" opacity=".8"/><rect x="2" y="117" width="108" height="85" rx="4" fill="#e0ecdf"/><text x="55" y="155" text-anchor="middle" font-size="18" fill="#345b66" font-family="Arial">ÁGUA</text><text x="55" y="178" text-anchor="middle" font-size="13" fill="#345b66" font-family="Arial">500 ml</text></g>'
    elif pid==6:
        drawing='<ellipse cx="275" cy="282" rx="165" ry="35" fill="#ddd0b3"/>'
        for x,y in [(130,170),(210,145),(290,160),(180,225),(280,225),(340,210)]:drawing+=f'<path d="M{x} {y+60}L{x+50} {y-25}L{x+100} {y+65}Z" fill="#e6ae46" stroke="#b47d2e" stroke-width="4"/>'
        drawing+='<ellipse cx="397" cy="270" rx="48" ry="23" fill="#f4e8ce"/><ellipse cx="397" cy="264" rx="39" ry="15" fill="#eaa01e"/>'
    else:
        drawing='<path d="M167 85H373L355 310H185Z" fill="'+('#693c29' if pid==10 else '#bc3d58')+'"/><text x="270" y="145" text-anchor="middle" font-family="Arial" font-size="23" fill="#fff0d6">'+('CHOCOLATE' if pid==10 else 'DOCES')+'</text>'
        for i in range(24):
            x=random.uniform(200,340);y=random.uniform(180,275)
            drawing+=f'<ellipse cx="{x}" cy="{y}" rx="12" ry="8" fill="{random.choice(["#d74443","#f3c046","#61a475","#6f9dc8","#e28743"])}"/>'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 380"><defs><radialGradient id="bg"><stop stop-color="#655344"/><stop offset="1" stop-color="#292322"/></radialGradient></defs><rect width="560" height="380" fill="url(#bg)"/><ellipse cx="280" cy="327" rx="180" ry="22" fill="#171314" opacity=".5"/>{drawing}<text x="280" y="363" text-anchor="middle" font-family="Arial" font-size="9" letter-spacing="2" fill="#c9b5a3">IMAGEM ILUSTRATIVA · CINESENAI</text></svg>'
    (ROOT/f'produto-{pid}.svg').write_text(svg,encoding='utf-8')
print('11 ilustrações de produtos criadas.')
