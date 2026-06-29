from app.common.models.value_objects import Phone


def test_phone_value_object_does_not_prefix_default_country_code():
    assert str(Phone(value="08012345678")) == "08012345678"


def test_phone_value_object_preserves_explicit_country_code():
    assert str(Phone(value="+2348012345678")) == "+2348012345678"
