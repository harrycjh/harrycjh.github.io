#!/usr/bin/env python3
from pathlib import Path
import re
import sys


INDEX_PATH = Path("/Users/chujianhe/.openclaw/workspace-taizi/index.html")


def main() -> int:
    text = INDEX_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"const\s+ENABLE_OBSTACLE_OVERLAY_LAYER\s*=\s*(true|false)\s*;",
        text,
    )
    if not match:
        print("FAIL: ENABLE_OBSTACLE_OVERLAY_LAYER not found")
        return 1
    value = match.group(1)
    if value != "true":
        print(
            "FAIL: obstacle overlay layer is globally disabled; "
            "toggle button cannot show collision cells"
        )
        return 1
    print("PASS: obstacle overlay layer is enabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
