from pathlib import Path

import pytest

from ams2_ai.xml.reader import load_document
from ams2_ai.xml.writer import save_document

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "docs" / "example_ai_files"


@pytest.mark.parametrize(
    "filename",
    [
        "StockCarV8.xml",
        "F-Classic_Gen4.xml",
        "LMDh.xml",
    ],
)
def test_roundtrip_example_files(filename: str, tmp_path: Path):
    source = EXAMPLES_DIR / filename
    if not source.exists():
        pytest.skip(f"Example file missing: {source}")

    document = load_document(source)
    original_count = len(document.drivers)
    assert original_count > 0

    target = tmp_path / filename
    save_document(document, target)

    reloaded = load_document(target)
    assert len(reloaded.drivers) == original_count

    first_original = document.drivers[0]
    first_reloaded = reloaded.drivers[0]
    assert first_reloaded.livery_name == first_original.livery_name
    assert first_reloaded.set_fields == first_original.set_fields
