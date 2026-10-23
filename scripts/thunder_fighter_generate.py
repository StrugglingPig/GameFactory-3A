#!/usr/bin/env python3
"""Generate deterministic GameFactory ships for the Thunder Fighter PoC."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from operators.gen_3d_object.operator import Gen3DObjectOperator  # noqa: E402


MATERIALS = {
    "player": {"base_color": [0.08, 0.24, 0.36, 1.0], "roughness": 0.34, "metallic": 0.72},
    "player-accent": {"base_color": [0.05, 0.72, 0.86, 1.0], "roughness": 0.24, "metallic": 0.58},
    "enemy": {"base_color": [0.30, 0.05, 0.06, 1.0], "roughness": 0.44, "metallic": 0.48},
    "enemy-accent": {"base_color": [0.95, 0.23, 0.09, 1.0], "roughness": 0.35, "metallic": 0.20},
    "boss": {"base_color": [0.14, 0.08, 0.22, 1.0], "roughness": 0.48, "metallic": 0.52},
    "boss-accent": {"base_color": [0.72, 0.18, 0.88, 1.0], "roughness": 0.28, "metallic": 0.64},
    "canopy": {"base_color": [0.08, 0.62, 0.76, 1.0], "roughness": 0.12, "metallic": 0.08},
}


SPECS = {
    "player": {
        "subject": "CX-9 thunder interceptor player fighter",
        "asset_type": "vehicle",
        "height_metres": 0.30,
        "forward": "+z",
        "parts": [
            {"id": "fuselage", "kind": "box", "size": [0.56, 0.18, 1.30], "at": [0, 0.14, 0], "material": "player"},
            {"id": "nose", "kind": "box", "size": [0.34, 0.14, 0.42], "at": [0, 0.13, 0.82], "material": "player-accent", "chamfer": 0.20},
            {"id": "wings", "kind": "box", "size": [1.86, 0.08, 0.52], "at": [0, 0.10, -0.12], "material": "player"},
            {"id": "wing-tips-l", "kind": "box", "size": [0.16, 0.10, 0.78], "at": [-0.84, 0.10, -0.08], "material": "player-accent"},
            {"id": "wing-tips-r", "kind": "box", "size": [0.16, 0.10, 0.78], "at": [0.84, 0.10, -0.08], "material": "player-accent"},
            {"id": "canopy", "kind": "sphere", "size": [0.28, 0.16, 0.40], "at": [0, 0.25, 0.34], "material": "canopy"},
            {"id": "engine-l", "kind": "box", "size": [0.22, 0.18, 0.46], "at": [-0.25, 0.15, -0.72], "material": "player-accent"},
            {"id": "engine-r", "kind": "box", "size": [0.22, 0.18, 0.46], "at": [0.25, 0.15, -0.72], "material": "player-accent"},
        ],
    },
    "enemy": {
        "subject": "VX raider enemy drone",
        "asset_type": "vehicle",
        "height_metres": 0.40,
        "forward": "+z",
        "parts": [
            {"id": "core", "kind": "sphere", "size": [0.62, 0.28, 0.72], "at": [0, 0.18, 0], "material": "enemy"},
            {"id": "wing-l", "kind": "box", "size": [0.78, 0.10, 0.34], "at": [-0.62, 0.12, -0.02], "material": "enemy"},
            {"id": "wing-r", "kind": "box", "size": [0.78, 0.10, 0.34], "at": [0.62, 0.12, -0.02], "material": "enemy"},
            {"id": "blade-l", "kind": "box", "size": [0.18, 0.08, 0.92], "at": [-1.00, 0.09, -0.08], "material": "enemy-accent"},
            {"id": "blade-r", "kind": "box", "size": [0.18, 0.08, 0.92], "at": [1.00, 0.09, -0.08], "material": "enemy-accent"},
            {"id": "eye", "kind": "sphere", "size": [0.18, 0.12, 0.20], "at": [0, 0.36, 0.28], "material": "enemy-accent"},
        ],
    },
    "boss": {
        "subject": "Dreadnought thunder boss warship",
        "asset_type": "vehicle",
        "height_metres": 0.72,
        "forward": "+z",
        "parts": [
            {"id": "hull", "kind": "box", "size": [2.40, 0.34, 2.00], "at": [0, 0.28, 0], "material": "boss"},
            {"id": "wing", "kind": "box", "size": [4.70, 0.20, 0.92], "at": [0, 0.20, -0.10], "material": "boss"},
            {"id": "pod-l", "kind": "box", "size": [0.86, 0.44, 2.30], "at": [-1.60, 0.30, 0.06], "material": "boss-accent", "chamfer": 0.18},
            {"id": "pod-r", "kind": "box", "size": [0.86, 0.44, 2.30], "at": [1.60, 0.30, 0.06], "material": "boss-accent", "chamfer": 0.18},
            {"id": "bridge", "kind": "box", "size": [0.70, 0.38, 0.70], "at": [0, 0.60, -0.36], "material": "boss-accent"},
            {"id": "core", "kind": "sphere", "size": [0.44, 0.26, 0.44], "at": [0, 0.23, 0.84], "material": "canopy"},
            {"id": "turret-l", "kind": "box", "size": [0.34, 0.30, 0.52], "at": [-1.20, 0.58, 0.52], "material": "boss-accent"},
            {"id": "turret-r", "kind": "box", "size": [0.34, 0.30, 0.52], "at": [1.20, 0.58, 0.52], "material": "boss-accent"},
        ],
    },
}


def generate_asset(operator: Gen3DObjectOperator, name: str) -> dict:
    spec = {"units": "metres", "materials": MATERIALS, **SPECS[name]}
    result = operator.run({"task_id": name, "spec": spec})
    glb_path = Path(result["glb_path"]).resolve()
    digest = hashlib.sha256(glb_path.read_bytes()).hexdigest()
    return {
        "taskId": name,
        "glbPath": str(glb_path),
        "sha256": digest,
        "bytes": glb_path.stat().st_size,
        "triangles": result["triangles"],
        "bounds": result["bounds"],
        "gatesOk": bool(result["gates"]["ok"]),
        "gates": result["gates"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    operator = Gen3DObjectOperator(model=None, output_dir=str(output_dir), default_game_id="_scratch")
    assets = {name: generate_asset(operator, name) for name in SPECS}
    manifest = {
        "schema": "thunder_fighter.assets.v1",
        "backend": "gamefactory3a.code_asset",
        "assets": assets,
    }
    manifest_path = output_dir / "thunder_fighter_assets.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifestPath": str(manifest_path),
        "assets": {name: {"glbPath": item["glbPath"], "sha256": item["sha256"], "bytes": item["bytes"], "triangles": item["triangles"], "gatesOk": item["gatesOk"]} for name, item in assets.items()},
    }, indent=2))
    return 0 if all(item["gatesOk"] for item in assets.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
