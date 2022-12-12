from domainmodel import Project
from microkit.utils import collect_cet_now


def test_from_attrubute_data():
    creation_time = collect_cet_now()
    proj = Project.from_attribute_data(
        name="Test 01",
        updated_by="pluto",
        updated_at=collect_cet_now()
    )
    assert "test-01" in proj.SK
    assert proj.updated_at == creation_time
