from ams2_ai.data import (
    get_track_meta,
    group_tracks_by_venue,
    load_tracks,
    track_display_label,
    track_search_blob,
    track_tab_label,
)


def test_every_track_has_meta():
    for code in load_tracks():
        meta = get_track_meta(code)
        assert meta is not None, code
        assert meta.code == code
        assert meta.venue.strip()
        assert meta.layout.strip()


def test_track_display_labels():
    assert track_display_label("Adelaide_Historic") == "Adelaide Historic 1988 (Adelaide_Historic)"
    assert track_display_label("BrandsHatch_GP") == "Brands Hatch Grand Prix (BrandsHatch_GP)"
    assert track_tab_label("Interlagos_GP") == "Interlagos Grand Prix"


def test_track_search_is_case_insensitive():
    blob = track_search_blob("BrandsHatch_GP")
    assert "brands hatch" in blob
    assert "brandshatch_gp" in blob


def test_group_tracks_by_venue():
    grouped = group_tracks_by_venue(["Adelaide_Historic", "Adelaide_Modern", "BrandsHatch_GP"])
    assert "Adelaide" in grouped
    assert len(grouped["Adelaide"]) == 2
    assert "Brands Hatch" in grouped
