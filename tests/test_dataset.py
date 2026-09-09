import pytest

from app.evaluation.dataset import DatasetCase, DatasetManifest, build_manifest, manifest_to_json
from app.scenarios.catalog import SCENARIOS


def test_dataset_case_normalizes_tags() -> None:
    case = DatasetCase("scenario", (" Production ", "production", "DB"))
    assert case.tags == ("db", "production")


def test_dataset_case_rejects_invalid_weight() -> None:
    with pytest.raises(ValueError, match="weight"):
        DatasetCase("scenario", weight=0)


def test_manifest_requires_cases() -> None:
    with pytest.raises(ValueError, match="at least one"):
        DatasetManifest("core", "1", ())


def test_manifest_rejects_duplicate_cases() -> None:
    case = DatasetCase("same")
    with pytest.raises(ValueError, match="duplicate"):
        DatasetManifest("core", "1", (case, case))


def test_manifest_fingerprint_is_stable() -> None:
    manifest = DatasetManifest(
        "core",
        "1",
        (DatasetCase("a", ("db",)), DatasetCase("b", ("cache",))),
    )
    assert manifest.fingerprint == manifest.fingerprint
    assert len(manifest.fingerprint) == 64


def test_manifest_selection_by_id_and_tag() -> None:
    manifest = DatasetManifest(
        "core",
        "1",
        (
            DatasetCase("a", ("db", "production")),
            DatasetCase("b", ("cache", "production")),
            DatasetCase("c", ("db",)),
        ),
    )
    selected = manifest.select(tags=("production",))
    assert [case.scenario_id for case in selected.cases] == ["a", "b"]
    selected = manifest.select(scenario_ids=("c",))
    assert [case.scenario_id for case in selected.cases] == ["c"]


def test_manifest_selection_rejects_empty_result() -> None:
    manifest = DatasetManifest("core", "1", (DatasetCase("a"),))
    with pytest.raises(ValueError, match="no cases"):
        manifest.select(scenario_ids=("missing",))


def test_manifest_resolves_catalog() -> None:
    catalog = {scenario.id: scenario for scenario in SCENARIOS}
    manifest = build_manifest("core", "1", SCENARIOS)
    resolved = manifest.scenarios(catalog)
    assert tuple(item.id for item in resolved) == tuple(item.id for item in SCENARIOS)


def test_manifest_rejects_unknown_catalog_scenario() -> None:
    manifest = DatasetManifest("core", "1", (DatasetCase("missing"),))
    with pytest.raises(KeyError, match="Unknown"):
        manifest.scenarios({})


def test_manifest_json_contains_fingerprint() -> None:
    manifest = DatasetManifest("core", "1", (DatasetCase("a"),))
    payload = manifest_to_json(manifest)
    assert '"fingerprint"' in payload
    assert '"scenario_id": "a"' in payload


def test_manifest_requires_name_and_version() -> None:
    case = DatasetCase("a")
    with pytest.raises(ValueError):
        DatasetManifest("", "1", (case,))
    with pytest.raises(ValueError):
        DatasetManifest("core", "", (case,))
