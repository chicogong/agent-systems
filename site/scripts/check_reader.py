"""Browser smoke checks for reading, sharing, figures and offline entry points.

Install site/requirements-test.txt and run playwright install chromium first.
Use --export-share-card to regenerate the tracked 1200x630 artwork, separately
from tests. Screenshots and reports go to ignored output/review/ by default.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def check_reader(origin: str, output: Path, live: bool, channel: str | None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel=channel)
        errors: list[str] = []
        for width in (390, 1440):
            context = browser.new_context(viewport={"width": width, "height": 920})
            if not live:
                context.add_init_script("""
                    Object.defineProperty(navigator, 'share', {value: undefined, configurable: true});
                    Object.defineProperty(navigator, 'clipboard', {value: {
                        writeText: async text => {window.readerTestCopied = text}
                    }, configurable: true});
                """)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            # QA visits are not promotion traffic, even when testing production.
            page.route("**/_vercel/insights/**", lambda route: route.abort())
            page.goto(origin, wait_until="networkidle")
            expect(page.get_by_role("heading", name="图解 Agent 系统", exact=True)).to_be_visible()
            expect(page.get_by_role("link", name="从一张图开始读 →")).to_be_visible()
            assert page.locator('.topic-card').count() == 3
            assert page.locator('meta[property="og:image"]').get_attribute("content").endswith('/assets/share/book.png')
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"Overflow at {width}px"
            for image in page.locator('.reader-hero img, .topic-card img').all():
                assert image.evaluate("image => image.complete && image.naturalWidth > 0"), "Broken entry artwork"
            page.screenshot(path=str(output / f"reader-home-{width}.png"), full_page=False)
            page.get_by_role("link", name="从一张图开始读 →").click()
            expect(page.get_by_role("heading", level=1)).to_contain_text("Agent")
            page.get_by_role("button", name="放大图稿：", exact=False).first.click()
            expect(page.get_by_role("dialog", name="图稿细读")).to_be_visible()
            page.get_by_role("button", name="关闭大图").press("Escape")
            expect(page.get_by_role("dialog", name="图稿细读")).not_to_be_visible()
            if not live:
                page.goto(origin.rstrip('/') + '/concepts/agent-loop?private=not-to-share#sample', wait_until='networkidle')
                page.get_by_role('button', name='分享这一页').click()
                expect(page.get_by_role('status')).to_contain_text('链接已复制')
                assert page.evaluate('window.readerTestCopied') == origin.rstrip('/') + '/concepts/agent-loop'
            page.goto(origin.rstrip('/') + '/downloads', wait_until="networkidle")
            expect(page.get_by_role("heading", level=1)).to_have_text("下载与离线阅读")
            expect(page.get_by_text('打开文件夹作为仓库', exact=False)).to_be_visible()
            page.screenshot(path=str(output / f"reader-downloads-{width}.png"), full_page=False)
            if page.get_by_role('link', name='下载 Markdown 阅读包（ZIP）').count():
                href = page.get_by_role('link', name='下载 Markdown 阅读包（ZIP）').get_attribute('href')
                assert context.request.get(origin.rstrip('/') + href).status == 200
            context.close()
        browser.close()
        if errors:
            raise AssertionError("Reader browser errors: " + "; ".join(errors))
    print(json.dumps({"origin": origin, "viewports": [390, 1440], "home": "pass", "figures": "pass", "sharing": "live-no-copy" if live else "pass", "offline": "pass", "browserErrors": errors}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:4173")
    parser.add_argument("--output", type=Path, default=ROOT / "output/review")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--export-share-card", action="store_true")
    parser.add_argument("--channel", help="Use an installed browser, e.g. chrome; omit for Playwright Chromium")
    args = parser.parse_args()
    if args.export_share_card:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, channel=args.channel)
            page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
            page.goto((ROOT / 'site/assets/book-share.html').as_uri(), wait_until="networkidle")
            page.screenshot(path=str(ROOT / 'site/assets/book-share.png'))
            browser.close()
        print("Exported share artwork: site/assets/book-share.png (1200x630)")
    else:
        check_reader(args.url, args.output, args.live, args.channel)
