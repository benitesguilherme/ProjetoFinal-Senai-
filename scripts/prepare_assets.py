"""Baixa os materiais visuais identificados no catálogo de referência."""

from concurrent.futures import ThreadPoolExecutor

from pathlib import Path

from urllib.request import urlopen, Request

import json



ROOT = Path(__file__).resolve().parents[1]

ASSETS = {

    'imitacao-poster.jpg': 'https://image.tmdb.org/t/p/w500/zSqJ1qFq8NXFfi7JeIYMlzyR0dx.jpg',

    'imitacao-banner.jpg': 'https://image.tmdb.org/t/p/w1280/8FCHJ21JBQOgATY2WI8vwYAiXg8.jpg',

    'oppenheimer-poster.jpg': 'https://image.tmdb.org/t/p/w500/ptpr0kGAckfQkJeJIt8st5dglvd.jpg',

    'interestelar-poster.jpg': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',

    'divertida-poster.jpg': 'https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg',

    'duna-poster.jpg': 'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg',

    'interestelar-banner.jpg': 'https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg',


    'pipoca.jpg': 'https://images.unsplash.com/photo-1578849278619-e73505e9610f?auto=format&fit=crop&w=1000&q=85',

    'teatro.jpg': 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&w=1000&q=85',

}



def download(item):

    name, url = item

    dest = ROOT / 'static' / 'images' / name

    if dest.exists():

        return name, 'existing'

    try:

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        data = urlopen(req, timeout=30).read()

        from PIL import Image

        from io import BytesIO

        image = Image.open(BytesIO(data))

        image.thumbnail((1920, 1200))

        image.convert('RGB').save(dest, quality=87)

        return name, f'{image.size}, {dest.stat().st_size} bytes'

    except Exception as exc:

        return name, str(exc)



if __name__ == '__main__':

    (ROOT / 'static' / 'images').mkdir(exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as pool:

        for result in pool.map(download, ASSETS.items()):

            print(result)

    (ROOT / 'static' / 'images' / 'sources.json').write_text(json.dumps(ASSETS, indent=2), encoding='utf-8')
