from actions.actions import _suggest_outfit


def test_outfit_hot():
    assert "Hot" in _suggest_outfit(30, "Sunny")


def test_outfit_rain():
    assert "umbrella" in _suggest_outfit(12, "Light rain")


def test_outfit_freezing():
    assert "Freezing" in _suggest_outfit(-5, "Snow")
