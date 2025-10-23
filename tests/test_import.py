def test_import_waymore():
    import importlib

    m = importlib.import_module("waymore")
    assert m is not None
