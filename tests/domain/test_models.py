from datetime import UTC, datetime

from axenda.domain.models import City, Event, EventType, Venue


class TestEventType:
    def test_all_types_have_values(self) -> None:
        assert EventType.MUSICA.value == "Música"
        assert EventType.TEATRO.value == "Teatro"
        assert EventType.OTROS.value == "Otros"

    def test_create_from_string(self) -> None:
        assert EventType("Música") == EventType.MUSICA

    def test_unknown_type_raises(self) -> None:
        import pytest
        with pytest.raises(ValueError):
            EventType("Fiestón")


class TestCity:
    def test_create_city(self) -> None:
        city = City(id=1, name="Gijón", name_normalized="gijon", region="Asturias")
        assert city.name == "Gijón"
        assert city.default_locale == "es"
        assert city.timezone == "Europe/Madrid"

    def test_city_asturian_locale(self) -> None:
        city = City(
            id=1,
            name="Gijón",
            name_normalized="gijon",
            region="Asturias",
            default_locale="ast",
        )
        assert city.default_locale == "ast"


class TestVenue:
    def test_create_venue_minimal(self) -> None:
        venue = Venue(id=1, name="Teatro Jovellanos", city_id=1)
        assert venue.name == "Teatro Jovellanos"
        assert venue.address is None

    def test_create_venue_full(self) -> None:
        venue = Venue(
            id=1,
            name="Teatro Jovellanos",
            address="Calle A, 1",
            url="https://example.com",
            city_id=1,
        )
        assert venue.address == "Calle A, 1"


class TestEvent:
    def test_create_event_minimal(self) -> None:
        event = Event(
            id=1,
            title="Concierto de prueba",
            event_type=EventType.MUSICA,
            event_date=datetime(2026, 6, 1, tzinfo=UTC),
            source="test",
            source_id="123",
            city_id=1,
        )
        assert event.title == "Concierto de prueba"
        assert event.event_type == EventType.MUSICA
        assert event.genres == []

    def test_create_event_full(self) -> None:
        venue = Venue(id=1, name="Sala X", city_id=1)
        event = Event(
            id=1,
            title="Conciertazo",
            event_type=EventType.MUSICA,
            description="Un gran concierto",
            event_date=datetime(2026, 6, 1, 21, 0, tzinfo=UTC),
            price_info="15€",
            url="https://example.com",
            source="test",
            source_id="abc",
            venue_id=1,
            city_id=1,
            genres=["rock", "pop"],
        )
        assert event.genres == ["rock", "pop"]
        assert event.price_info == "15€"
