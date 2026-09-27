"""Batch export using excalidraw-agent's unchanged native renderer HTML.

Only static jsDelivr transport is cached. No alternate SVG renderer or font
substitution is used. Requires the renderer skill's Playwright environment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def export(renderer: Path, slugs: list[str], cache: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=4)

        def static_asset(route):
            url = route.request.url
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or parsed.netloc != 'cdn.jsdelivr.net':
                route.abort()
                return
            target = cache / hashlib.sha256(url.encode()).hexdigest()
            if not target.is_file():
                response = subprocess.run(
                    ['curl', '--fail', '--silent', '--show-error', '--location',
                     '--max-time', '30', '--retry', '1', url],
                    check=True, capture_output=True,
                )
                target.write_bytes(response.stdout)
                print('Cached static asset:', url, flush=True)
            mime = 'font/woff2' if parsed.path.endswith('.woff2') else 'text/javascript'
            route.fulfill(body=target.read_bytes(), content_type=mime,
                          headers={'access-control-allow-origin': '*'})

        page.route('https://cdn.jsdelivr.net/**', static_asset)
        page.goto(renderer.resolve().as_uri())
        page.wait_for_function('window.rendererReady === true', timeout=120_000)
        error = page.evaluate('window.rendererError || null')
        if error:
            raise RuntimeError(error)
        for slug in slugs:
            if Path(slug).name != slug or slug in ('.', '..'):
                raise ValueError('Expected a figure directory name, not a path')
            folder = ROOT / 'figures' / slug
            scene = json.loads((folder / 'scene.excalidraw').read_text())
            result = page.evaluate('async scene => window.exportScene(scene, 6000)', scene)
            if not result.get('ok'):
                raise RuntimeError(result)
            page.set_viewport_size({'width': max(800, int(result['width'])+32),
                                    'height': max(600, int(result['height'])+32)})
            drawing = page.locator('#drawing > svg')
            svg = drawing.evaluate('node => new XMLSerializer().serializeToString(node)')
            (folder / 'diagram.svg').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'+svg+'\n')
            drawing.screenshot(path=str(folder / 'preview.png'), animations='disabled')
            print('Exported native SVG and 4x PNG:', slug, flush=True)
        browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer', type=Path, required=True)
    parser.add_argument('--cache', type=Path, default=ROOT / 'tmp' / 'native-export-cache')
    parser.add_argument('figures', nargs='+')
    args = parser.parse_args()
    export(args.renderer, args.figures, args.cache)
