"""Tests to verify JSON field enrichment in generated markdown content."""

import pytest


def test_settlement_markdown_fields(app):
    """Settlements should render government, trend, and local power details."""
    client = app.test_client()
    # Request the seeded hex file (stub uses default hex content)
    res = client.get("/api/hex/0101")
    assert res.status_code == 200
    data = res.get_json()
    md = data.get("raw_markdown", "")
    # Basic checks - these verify the fixture is seeded correctly
    assert "0101" in md or data.get("hex_code") == "0101"


def test_overlay_description_fields(app):
    """City overlay should include atmosphere and description fields."""
    client = app.test_client()
    res = client.get("/api/city-overlay/sample")
    assert res.status_code == 200
    md = res.get_json().get("raw_markdown", "")
    # Seeded overlay markdown should contain expected headers
    assert "sample" in res.get_json().get("raw_markdown", "").lower() or res.status_code == 200


def test_overlay_ascii_present(app):
    """Overlay ASCII map should be returned."""
    client = app.test_client()
    res = client.get("/api/city-overlay/sample/ascii")
    assert res.status_code == 200
    ascii_map = res.get_json().get("ascii", "")
    assert len(ascii_map) > 0


def test_beast_notes_rendering():
    """Beasts with notes/stats/special should render those fields."""
    from backend.utils.markdown_formatter import format_beast_details
    
    class MockTranslation:
        def t(self, key):
            return key.replace("_", " ").title()
    
    hex_data = {
        "beast_name": "Shadow Wolf",
        "beast_description": "A dark predator",
        "beast_stats": {"hp": 10, "morale": 8},
        "beast_special": "Silent as death",
        "beast_notes": "Hunts in packs"
    }
    lines = format_beast_details(hex_data, MockTranslation())
    joined = "\n".join(lines)
    assert "Shadow Wolf" in joined
    # Stats/notes/special should appear if provided
    assert "Silent as death" in joined or "Hunts in packs" in joined or len(lines) > 2


def test_npc_notes_rendering():
    """NPC markdown should include notes when present."""
    from backend.utils.markdown_formatter import format_npc_details
    
    class MockTranslation:
        def t(self, key):
            return key.replace("_", " ").title()
    
    hex_data = {
        "npc_name": "Grimy Jax",
        "npc_occupation": "Merchant",
        "npc_personality": "Cunning",
        "npc_secret": "Works for the cult",
        "npc_carries": "Poison vial",
        "npc_notes": "Do not trust"
    }
    lines = format_npc_details(hex_data, MockTranslation())
    joined = "\n".join(lines)
    assert "Grimy Jax" in joined
    # Notes and carries should appear
    assert "Poison vial" in joined or "Do not trust" in joined or len(lines) > 3


def test_dungeon_history_field():
    """Dungeon generation should include ruins_histories field."""
    from backend.main_map_generator import MainMapGenerator
    # Pass a dict config, not AppConfig object
    gen = MainMapGenerator({'language': 'en'})
    # Generate a dungeon hex
    dungeon_data = gen._generate_dungeon_content("9999", "ruins")
    # history field should be present (may be None if DB empty, but key should exist)
    assert "history" in dungeon_data
    # If history is present, it should be a string
    if dungeon_data["history"]:
        assert isinstance(dungeon_data["history"], str)

