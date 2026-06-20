from ams2_ai.data import load_countries, load_tracks, load_vehicle_classes


def test_reference_data_loads():
    countries = load_countries()
    tracks = load_tracks()
    classes = load_vehicle_classes()

    assert len(countries) > 0
    assert len(tracks) > 0
    assert len(classes) > 0
    assert all(len(code) == 3 for code in countries[:5])
