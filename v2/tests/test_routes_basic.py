from zipfile import ZipFile
from io import BytesIO


def test_health(app):
    client = app.test_client()
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True


def test_languages(app):
    client = app.test_client()
    res = client.get("/api/languages")
    data = res.get_json()
    assert data["current"] == "en"
    assert "en" in data["languages"]


def test_hex_fetch(app):
    client = app.test_client()
    res = client.get("/api/hex/0101")
    data = res.get_json()
    assert res.status_code == 200
    assert data["hex_code"] == "0101"
    assert "raw_markdown" in data


def test_map_ascii(app):
    client = app.test_client()
    res = client.get("/api/map")
    data = res.get_json()
    assert res.status_code == 200
    assert "ascii" in data
    assert data.get("language") == "en"


def test_export(app):
    client = app.test_client()
    res = client.get("/api/export")
    assert res.status_code == 200
    # ensure zip content is valid
    zf = ZipFile(BytesIO(res.data))
    names = zf.namelist()
    assert any(name.endswith("hex_0101.md") for name in names)


def test_set_language_invalid(app):
    client = app.test_client()
    res = client.post("/api/set-language", json={"language": "zz"})
    assert res.status_code == 400
    data = res.get_json()
    assert "supported" in data


def test_set_language_success(app):
    client = app.test_client()
    res = client.post("/api/set-language", json={"language": "pt"})
    data = res.get_json()
    assert res.status_code == 200
    assert data["success"] is True
    assert data["language"] == "pt"


def test_overlays_list_and_get(app):
    client = app.test_client()
    res = client.get("/api/city-overlays")
    assert res.status_code == 200
    overlays = res.get_json().get("overlays", [])
    assert any(o["name"] == "sample" for o in overlays)

    res2 = client.get("/api/city-overlay/sample")
    assert res2.status_code == 200
    assert "raw_markdown" in res2.get_json()

    res3 = client.get("/api/city-overlay/sample/ascii")
    assert res3.status_code == 200
    assert "ascii" in res3.get_json()


def test_import(app, tmp_path):
    # Build a minimal zip with a hex file
    hex_dir = tmp_path / "dying_lands_output" / "en" / "hexes"
    hex_dir.mkdir(parents=True, exist_ok=True)
    (hex_dir / "hex_9999.md").write_text("# Hex 9999\n\n**Terrain:** Plains\n\n## Encounter\nImported", encoding="utf-8")

    mem = BytesIO()
    with ZipFile(mem, "w") as zf:
        for file in hex_dir.rglob("*"):
            zf.write(file, arcname=str(file.relative_to(tmp_path)))
    mem.seek(0)

    client = app.test_client()
    res = client.post("/api/import", data={"file": (mem, "import.zip")}, content_type="multipart/form-data")
    assert res.status_code == 200
    data = res.get_json()
    assert data["ok"] is True

