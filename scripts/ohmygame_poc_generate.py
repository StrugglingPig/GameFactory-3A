#!/usr/bin/env python3
"""Generate a deterministic GameFactory GLB for the OhMyGame local PoC."""

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


def build_spec() -> dict:
    return {
        "subject": "wooden supply crate",
        "units": "metres",
        "forward": "+z",
        "asset_type": "prop",
        "height_metres": 0.68,
        "parts": [
            {"id": "body", "kind": "box", "size": [0.60, 0.52, 0.60], "at": [0, 0.26, 0], "material": "wood"},
            {"id": "lid", "kind": "box", "size": [0.64, 0.08, 0.64], "at": [0, 0.60, 0], "material": "wood-dark"},
            {"id": "band-left", "kind": "box", "size": [0.05, 0.56, 0.64], "at": [-0.26, 0.30, 0], "material": "metal"},
            {"id": "band-right", "kind": "box", "size": [0.05, 0.56, 0.64], "at": [0.26, 0.30, 0], "material": "metal"},
        ],
        "materials": {
            "wood": {"base_color": [0.45, 0.24, 0.10, 1.0], "roughness": 0.82, "metallic": 0.0},
            "wood-dark": {"base_color": [0.28, 0.14, 0.06, 1.0], "roughness": 0.88, "metallic": 0.0},
            "metal": {"base_color": [0.24, 0.25, 0.27, 1.0], "roughness": 0.55, "metallic": 0.65},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--task-id", default="ohmygame_poc_crate")
    args = parser.parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    operator = Gen3DObjectOperator(model=None, output_dir=str(output_dir), default_game_id="_scratch")
    result = operator.run({"task_id": args.task_id, "spec": build_spec()})
    glb_path = Path(result["glb_path"]).resolve()
    digest = hashlib.sha256(glb_path.read_bytes()).hexdigest()
    manifest = {
        "schema": "gamefactory3a.asset.v1",
        "assetId": args.task_id,
        "kind": "3d_object",
        "source": {
            "pipeline": "3d_object",
            "backend": "code_asset",
            "model": "deterministic-spec",
            "prompt": build_spec()["subject"],
        },
        "files": {
            "glb": {
                "path": glb_path.name,
                "sha256": digest,
                "size": glb_path.stat().st_size,
            }
        },
        "validation": {
            "specOk": result["spec_ok"],
            "gates": result["gates"],
            "triangles": result["triangles"],
            "bounds": result["bounds"],
            "partIds": result["part_ids"],
        },
        "engineHints": {
            "upAxis": "y",
            "frontAxis": "+z",
            "metersPerUnit": 1,
        },
    }
    manifest_path = output_dir / "gamefactory_asset.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "glbPath": str(glb_path),
        "manifestPath": str(manifest_path),
        "sha256": digest,
        "bytes": glb_path.stat().st_size,
        "triangles": result["triangles"],
        "gatesOk": bool(result["gates"]["ok"]),
    }, indent=2))
    return 0 if result["gates"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
