"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from terrain.web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific -----------------------------------------------------------------------------
import json  # noqa: E402

import numpy as np  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "terrain_reference.json"


def test_info_from_package():
    d = client.get("/api/info").json()
    assert d["defaults"]["size"] == 512 and d["defaults"]["season"] == "summer"
    assert [s["key"] for s in d["seasons"]] == ["spring", "summer", "fall", "winter"]
    assert len(d["features"]) == d["counts"]["features"] == 7


def test_colormaps_have_256_entries():
    d = client.get("/api/colormaps").json()
    assert len(d["terrain"]) == len(d["YlGnBu"]) == 256


def test_reference_is_deterministic():
    a = client.get("/api/reference/winter-seed-7").json()
    b = client.get("/api/reference/winter-seed-7").json()
    assert a == b and len(a["height"]) == 96 * 96 and len(a["colors"]) == 96 * 96
    assert a["params"]["snow_level"] == 0.85 and abs(a["snow_level"] - 0.68) < 1e-12


def test_generate_post_and_limits():
    r = client.post("/api/generate", json={"seed": 5, "params": {"size": 32, "season": "fall"}})
    assert r.status_code == 200 and len(r.json()["height"]) == 32 * 32
    assert client.post("/api/generate", json={"seed": 5, "params": {"size": 4000}}).status_code == 422
    assert client.post("/api/generate", json={"seed": -1}).status_code == 422
    assert client.get("/api/reference/nope").status_code == 404


def _close(a, b):
    np.testing.assert_allclose(np.asarray(a, float), np.asarray(b, float), rtol=1e-9, atol=1e-10)


def test_fixture_is_current():
    """tests/fixtures/terrain_reference.json (used by the JS node tests) matches the Python code today.
    Floats with a tolerance (libm differs in the last digit between macOS and Linux)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_terrain_fixture
    new, old = make_terrain_fixture.build_fixture(), json.loads(FIXTURE.read_text())
    assert new["defaults"] == old["defaults"] and new["features"] == old["features"]
    for a, b in zip(new["rng"], old["rng"]):
        assert a["seedseq"] == b["seedseq"] and a["raw"] == b["raw"]
        _close(a["random"] + a["normal"], b["random"] + b["normal"])
    _close(new["noise_32_f4_seed3"], old["noise_32_f4_seed3"])
    for a, b in zip(new["cases"], old["cases"]):
        assert a["params"] == b["params"] and a["palette"] == b["palette"]
        mism = sum(x != y for x, y in zip(a["colors"], b["colors"]))
        assert mism <= len(a["colors"]) // 500, (a["name"], mism)
        for key in ("base_height", "height", "moisture"):
            if isinstance(a[key], list):
                _close(a[key], b[key])
            else:
                _close(a[key]["values"], b[key]["values"])
        _close(list(a["mask_sums"].values()), list(b["mask_sums"].values()))
