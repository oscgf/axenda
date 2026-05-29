from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class DateRange:
    date_from: datetime
    date_to: datetime

    def __post_init__(self) -> None:
        if self.date_from > self.date_to:
            raise ValueError(f"date_from ({self.date_from}) must be <= date_to ({self.date_to})")

    @classmethod
    def this_weekend(cls, reference_date: datetime | None = None) -> "DateRange":
        today = (reference_date or datetime.now(UTC)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        friday = today + timedelta(days=(4 - today.weekday()) % 7)
        sunday = friday + timedelta(days=2, hours=23, minutes=59, seconds=59)
        return cls(date_from=friday, date_to=sunday)

    @classmethod
    def this_week(cls, reference_date: datetime | None = None) -> "DateRange":
        today = (reference_date or datetime.now(UTC)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return cls(date_from=monday, date_to=sunday)

    @classmethod
    def today(cls, reference_date: datetime | None = None) -> "DateRange":
        today = (reference_date or datetime.now(UTC)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = today.replace(hour=23, minute=59, second=59)
        return cls(date_from=today, date_to=end)

    def __contains__(self, dt: datetime) -> bool:
        return self.date_from <= dt <= self.date_to


@dataclass(frozen=True)
class Locale:
    code: str

    def __post_init__(self) -> None:
        if self.code not in ("es", "ast"):
            raise ValueError(f"Unsupported locale: {self.code}. Supported: es, ast")

    @property
    def is_asturian(self) -> bool:
        return self.code == "ast"

    @property
    def is_spanish(self) -> bool:
        return self.code == "es"
