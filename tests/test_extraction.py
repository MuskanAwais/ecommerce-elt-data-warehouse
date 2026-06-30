import pathlib
import json
import pytest

from extraction import extractor


def test_extraction_creates_files(tmp_path, monkeypatch):

    monkeypatch.setattr(extractor, "DATA_ROOT", tmp_path / "data")

    extractor.main()

    for entity in extractor.API_ENDPOINTS.keys():

        pattern = f"data/raw/{entity}/*/*/*/{entity}_*.json"

        matches = list(tmp_path.glob(pattern))

        assert matches, f"No file generated for {entity}"

        with matches[-1].open() as f:
            payload = json.load(f)

            expected_key = (
                "products" if entity == "products"
                else "users" if entity == "customers"
                else "carts"
            )

            assert expected_key in payload