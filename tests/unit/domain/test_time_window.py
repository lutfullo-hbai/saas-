"""TimeWindow value object testlari."""

from datetime import datetime, time

import pytest

from src.domain.value_objects.time_window import TimeWindow


class TestTimeWindow:
    """TimeWindow value object testlari."""

    def test_creation(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 0))
        assert tw.start == time(9, 0)
        assert tw.end == time(10, 0)

    def test_start_after_end_raises(self):
        with pytest.raises(ValueError, match="Start vaqt end vaqtdan keyin"):
            TimeWindow(start=time(10, 0), end=time(9, 0))

    def test_contains_within_window(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 0))
        dt = datetime(2026, 1, 1, 9, 30)
        assert tw.contains(dt) is True

    def test_contains_at_start_boundary(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 0))
        dt = datetime(2026, 1, 1, 9, 0)
        assert tw.contains(dt) is True

    def test_contains_at_end_boundary(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 0))
        dt = datetime(2026, 1, 1, 10, 0)
        assert tw.contains(dt) is True

    def test_contains_outside_window(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 0))
        dt = datetime(2026, 1, 1, 8, 59)
        assert tw.contains(dt) is False

    def test_contains_after_window(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 0))
        dt = datetime(2026, 1, 1, 10, 1)
        assert tw.contains(dt) is False

    def test_duration_minutes(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 30))
        assert tw.duration_minutes() == 90.0

    def test_is_frozen(self):
        tw = TimeWindow(start=time(9, 0), end=time(10, 0))
        with pytest.raises(AttributeError):
            tw.start = time(8, 0)
