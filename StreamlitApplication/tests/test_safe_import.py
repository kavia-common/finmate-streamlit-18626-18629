def test_safe_import():
    import safe_import
    assert hasattr(safe_import, 'DATA_DIR')
    import pathlib, json
    p = pathlib.Path(safe_import.DATA_DIR) / 'data.json'
    assert p.exists()
    d = json.loads(p.read_text())
    assert isinstance(d, dict)
