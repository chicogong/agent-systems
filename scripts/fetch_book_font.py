"""Fetch pinned OFL text and code fonts used by the printable book."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "book" / ".cache" / "NotoSansSC.ttf"
REGULAR = FONT.with_name("NotoSansSC-Regular.ttf")
BOLD = FONT.with_name("NotoSansSC-Bold.ttf")
MONO = FONT.with_name("JetBrainsMono.ttf")
MONO_REGULAR = FONT.with_name("JetBrainsMono-Regular.ttf")
URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    "e44c4b011a820c2cbe2fd2cfa8052037d7edb571/"
    "ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
)
SHA256 = "a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da"
MONO_URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    "e44c4b011a820c2cbe2fd2cfa8052037d7edb571/"
    "ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"
)
MONO_SHA256 = "48715a42ec242c21e9f02692891e147d022299a52e48d5e413e1a942193ffeda"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(source: Path, url: str, sha256: str) -> bool:
    refreshed = not source.is_file() or digest(source) != sha256
    if refreshed:
        temporary = source.with_suffix(".download")
        try:
            urllib.request.urlretrieve(url, temporary)
            if digest(temporary) != sha256:
                raise ValueError(f"Font download failed SHA-256 verification: {source.name}")
            temporary.replace(source)
        finally:
            temporary.unlink(missing_ok=True)
    return refreshed


def name_is_correct(path: Path, weight: int) -> bool:
    if not path.is_file():
        return False
    font = TTFont(path)
    expected = "NotoSansSC-Regular" if weight == 400 else "NotoSansSC-Bold"
    result = font["name"].getDebugName(6) == expected and font["OS/2"].usWeightClass == weight
    font.close()
    return result


def set_static_names(font: TTFont, weight: int) -> None:
    style = "Regular" if weight == 400 else "Bold"
    values = {
        1: "Noto Sans SC",
        2: style,
        4: f"Noto Sans SC {style}",
        6: f"NotoSansSC-{style}",
        16: "Noto Sans SC",
        17: style,
    }
    name = font["name"]
    for record in list(name.names):
        if record.nameID in values:
            name.setName(values[record.nameID], record.nameID,
                         record.platformID, record.platEncID, record.langID)


def main() -> None:
    FONT.parent.mkdir(parents=True, exist_ok=True)
    refreshed = fetch(FONT, URL, SHA256)
    for weight, target in ((400, REGULAR), (700, BOLD)):
        if not refreshed and name_is_correct(target, weight):
            continue
        source = TTFont(FONT)
        instance = instantiateVariableFont(source, {"wght": weight}, inplace=False)
        set_static_names(instance, weight)
        instance.save(target)
        instance.close()
        source.close()
    mono_refreshed = fetch(MONO, MONO_URL, MONO_SHA256)
    if mono_refreshed or not MONO_REGULAR.is_file():
        source = TTFont(MONO)
        instance = instantiateVariableFont(source, {"wght": 400}, inplace=False)
        instance.save(MONO_REGULAR)
        instance.close()
        source.close()
    print(f"Verified OFL Noto Sans SC and JetBrains Mono: {FONT.parent}")


if __name__ == "__main__":
    main()
