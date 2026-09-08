"""Rebuild manifest.json and index.json from what is in birds/.

Run by the index workflow on every push to main, so a contribution only ever
adds files - birds/<key>.png, and optionally birds/<key>.json beside it with
its manifest entry - and nothing two pull requests could both edit. A plate
with no sidecar is recorded as {"source": "generated"}, which is what every
plate here is. Standard library only; this repository has no dependencies.

    python3 tools/build_index.py
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMBERED = re.compile(r"-(\d+)$")


def main() -> None:
    manifest, birds = {}, {}
    for png in sorted((ROOT / "birds").glob("*.png")):
        entry = {"source": "generated"}
        sidecar = png.with_suffix(".json")
        if sidecar.exists():
            try:
                data = json.loads(sidecar.read_text())
                if isinstance(data, dict):
                    entry = {**entry, **{k: v for k, v in data.items() if isinstance(v, (str, int, float, bool))}}
            except ValueError:
                pass
        manifest[f"birds/{png.name}"] = entry
        birds.setdefault(NUMBERED.sub("", png.stem), []).append(
            {"file": f"birds/{png.name}", "sha256": hashlib.sha256(png.read_bytes()).hexdigest(), "source": entry["source"]}
        )
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (ROOT / "index.json").write_text(
        json.dumps({"version": 1, "license": "CC0-1.0", "birds": birds}, indent=2, sort_keys=True) + "\n"
    )
    print(f"{len(birds)} species, {len(manifest)} files")


if __name__ == "__main__":
    main()
