"""
Modeles SQLAlchemy pour la base de donnees.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserChoice(Base):
    """Enregistrement d'un choix utilisateur sur une borne."""

    __tablename__ = "user_choices"

    id = Column(Integer, primary_key=True, index=True)
    choix = Column(String(1), nullable=False, index=True)
    video = Column(Text, nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow, index=True)
    machine = Column(Text, nullable=False, index=True)

    def __repr__(self):
        return f"<UserChoice(id={self.id}, choix={self.choix}, machine={self.machine})>"


class Machine(Base):
    """Borne video enregistree dans le systeme."""

    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Machine(id={self.id}, name={self.name})>"
