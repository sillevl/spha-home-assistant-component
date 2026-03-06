import json
from pathlib import Path

from const import DOMAIN


def test_manifest_domain_matches_const_domain():
    manifest_path = Path(__file__).resolve().parents[1] / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["domain"] == DOMAIN
