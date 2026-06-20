from pathlib import Path

from ams2_ai.models.document import AIDocument
from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.driver_profile import DriverProfile, flatten_profiles
from ams2_ai.validation import validate_document
from ams2_ai.xml.reader import load_document
from ams2_ai.xml.writer import save_document, serialize_document

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "docs" / "example_ai_files"


def _sample_document() -> AIDocument:
    profile = DriverProfile(
        base=DriverEntry(
            livery_name="Test Livery",
            name="Test Driver",
            country="BRA",
        )
    )
    profile.base.set_fields.update({"name", "country"})
    document = AIDocument(set_name="Test Set")
    document.drivers = flatten_profiles([profile])
    document.sync_header_comment()
    return document


def test_internal_save_stores_xml_without_writing_file(tmp_path: Path):
    document = _sample_document()
    assert not validate_document(document)

    xml = serialize_document(document)
    document.commit_saved_state(xml)

    assert document.saved_xml == xml
    assert not document.dirty
    assert not (tmp_path / "custom_ai.xml").exists()


def test_export_writes_file_and_updates_saved_state(tmp_path: Path):
    document = _sample_document()
    target = tmp_path / "exported.xml"

    save_document(document, target)
    document.commit_saved_state(serialize_document(document))

    assert target.is_file()
    assert document.saved_xml is not None
    assert not document.dirty
    reloaded = load_document(target)
    assert reloaded.drivers[0].name == "Test Driver"


def test_serialize_matches_roundtrip_example(tmp_path: Path):
    source = EXAMPLES_DIR / "StockCarV8.xml"
    if not source.exists():
        return

    document = load_document(source)
    serialized = serialize_document(document)
    target = tmp_path / source.name
    target.write_text(serialized, encoding="utf-8")
    reloaded = load_document(target)
    assert len(reloaded.drivers) == len(document.drivers)
