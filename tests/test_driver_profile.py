from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.driver_profile import DriverProfile, flatten_profiles, group_drivers


def test_group_base_and_track_override():
    base = DriverEntry(livery_name="Team #1", name="Driver A", mode="custom")
    override = DriverEntry(
        livery_name="Team #1",
        tracks="Interlagos_GP",
        is_track_override=True,
        mode="custom",
    )
    override.set_ui_value("race_skill", 90)

    profiles = group_drivers([base, override])
    assert len(profiles) == 1
    assert profiles[0].base.entry_id == base.entry_id
    assert len(profiles[0].track_overrides) == 1


def test_add_track_copies_base_values():
    base = DriverEntry(livery_name="Team #1", mode="custom")
    base.set_ui_value("race_skill", 80)
    base.set_ui_value("aggression", 65)
    profile = DriverProfile(base=base, track_overrides=[])

    override = profile.add_track("Adelaide_Modern")
    assert override is not None
    assert override.get_ui_value("race_skill") == 80
    assert override.get_ui_value("aggression") == 65
    assert "race_skill" not in override.set_fields


def test_sync_track_overrides_from_base_updates_checked_fields():
    base = DriverEntry(livery_name="Team #1", mode="custom")
    base.set_ui_value("race_skill", 70)
    profile = DriverProfile(base=base, track_overrides=[])
    override = profile.add_track("Spa_Francorchamps_2020")
    assert override is not None
    override.set_ui_value("race_skill", 90)

    base.set_ui_value("race_skill", 85)
    profile.sync_track_overrides_from_base()

    assert override.get_ui_value("race_skill") == 85


def test_flatten_skips_empty_track_override():
    base = DriverEntry(livery_name="Team #1")
    empty_override = DriverEntry(
        livery_name="Team #1",
        tracks="Spa_Francorchamps_2020",
        is_track_override=True,
    )
    profile = DriverProfile(base=base, track_overrides=[empty_override])
    flat = flatten_profiles([profile])
    assert len(flat) == 1
