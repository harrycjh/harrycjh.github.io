"""One-off: crop suspected crystal OIDs from falan-atlas-00.png for visual check."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "assets" / "falan" / "object-map" / "atlases" / "falan-atlas-00.png"
MANIFEST = ROOT / "assets" / "falan" / "object-map" / "falan-city-1000-manifest.json"
OUT = ROOT / "assets" / "falan" / "object-map" / "debug-crystal-crops"


def main() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = m["assets"]
    oids = ["17236", "17237", "17238", "17239", "17240", "17241"]
    img = Image.open(ATLAS).convert("RGBA")
    OUT.mkdir(parents=True, exist_ok=True)
    for oid in oids:
        e = assets[oid]
        x, y, w, h = e["atlasX"], e["atlasY"], e["atlasW"], e["atlasH"]
        crop = img.crop((x, y, x + w, y + h))
        iid = e["imageId"]
        out = OUT / f"oid{oid}_imageId{iid}.png"
        crop.save(out)
    print("OK", len(oids), "png written under object-map/debug-crystal-crops/")


if __name__ == "__main__":
    main()
