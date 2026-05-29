from datetime import UTC, datetime, timedelta

import pytest
from axenda.domain.value_objects import DateRange, Locale


class TestDateRange:
    def test_create_valid_range(self) -> None:
        now = datetime.now(UTC)
        later = now + timedelta(days=1)
        dr = DateRange(date_from=now, date_to=later)
        assert dr.date_from == now
        assert dr.date_to == later

    def test_invalid_range_raises(self) -> None:
        now = datetime.now(UTC)
        earlier = now - timedelta(days=1)
        with pytest.raises(ValueError, match="must be <="):
            DateRange(date_from=now, date_to=earlier)

    def test_contains(self) -> None:
        now = datetime.now(UTC)
        dr = DateRange(
            date_from=now - timedelta(hours=1),
            date_to=now + timedelta(hours=1),
        )
        assert now in dr
        assert (now - timedelta(days=1)) not in dr

    def test_this_weekend(self) -> None:
        monday = datetime(2026, 6, 1, tzinfo=UTC)  # Monday
        dr = DateRange.this_weekend(reference_date=monday)
        assert dr.date_from.weekday() == 4  # Friday
        assert dr.date_to.weekday() == 6  # Sunday
        assert dr.date_from < dr.date_to

    def test_this_week(self) -> None:
        wednesday = datetime(2026, 6, 3, tzinfo=UTC)  # Wednesday
        dr = DateRange.this_week(reference_date=wednesday)
        assert dr.date_from.weekday() == 0  # Monday
        assert dr.date_to.weekday() == 6  # Sunday

    def test_today(self) -> None:
        ref = datetime(2026, 6, 15, 14, 30, tzinfo=UTC)
        dr = DateRange.today(reference_date=ref)
        assert dr.date_from.hour == 0
        assert dr.date_to.hour == 23
        assert dr.date_from.date() == dr.date_to.date() == ref.date()


class TestLocale:
    def test_valid_locales(self) -> None:
        es = Locale("es")
        ast = Locale("ast")
        assert es.is_spanish
        assert ast.is_asturian

    def test_invalid_locale_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported locale"):
            Locale("en")

    def test_is_spanish(self) -> None:
        assert Locale("es").is_spanish
        assert not Locale("ast").is_spanish

    def test_is_asturian(self) -> None:
        assert Locale("ast").is_asturian
        assert not Locale("es").is_asturian
