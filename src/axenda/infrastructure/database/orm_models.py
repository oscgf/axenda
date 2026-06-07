from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


event_genre = Table(
    "event_genre",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


class CityModel(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name_normalized: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, default="")
    timezone: Mapped[str] = mapped_column(String, default="Europe/Madrid")
    default_locale: Mapped[str] = mapped_column(String, default="es")

    venues: Mapped[list["VenueModel"]] = relationship(back_populates="city", lazy="selectin")
    events: Mapped[list["EventModel"]] = relationship(back_populates="city", lazy="selectin")


class VenueModel(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id"), nullable=False)

    city: Mapped["CityModel"] = relationship(back_populates="venues")
    events: Mapped[list["EventModel"]] = relationship(back_populates="venue", lazy="selectin")


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price_info: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, nullable=False)
    source_id: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String)
    venue_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("venues.id"))
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    venue: Mapped["VenueModel | None"] = relationship(back_populates="events")
    city: Mapped["CityModel"] = relationship(back_populates="events")
    genres: Mapped[list["GenreModel"]] = relationship(
        secondary=event_genre, back_populates="events", lazy="selectin"
    )


class GenreModel(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    events: Mapped[list["EventModel"]] = relationship(
        secondary=event_genre, back_populates="genres", lazy="selectin"
    )


class ScrapeLogModel(Base):
    __tablename__ = "scrape_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    events_found: Mapped[int] = mapped_column(Integer, default=0)
    events_new: Mapped[int] = mapped_column(Integer, default=0)
    events_updated: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
