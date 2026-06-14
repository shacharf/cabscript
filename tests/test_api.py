import pytest
from fastapi.testclient import TestClient
from cabinetry.app.main import app

client = TestClient(app)

SIMPLE_DSL = """use: euro_builtin_v1
material: plywood_18
space: niche 1000 x 2000 x 580
cabinet:
  type: built_in
  split: none
  base: legs 80
layout:
  main:
    columns:
      "*": shelves 2
"""


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_compile():
    resp = client.post("/api/compile", json={"dsl": SIMPLE_DSL})
    assert resp.status_code == 200
    data = resp.json()
    assert "project" in data
    assert "parts" in data["project"]
    assert len(data["project"]["parts"]) > 0


def test_render_glb():
    resp = client.post("/api/render.glb", json={"dsl": SIMPLE_DSL})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "model/gltf-binary"
    assert resp.content[:4] == b"glTF"


def test_cutlist():
    resp = client.post("/api/cutlist", json={"dsl": SIMPLE_DSL})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_stdlib():
    resp = client.get("/api/stdlib")
    assert resp.status_code == 200
    data = resp.json()
    assert "euro_builtin_v1" in data["standards"]
