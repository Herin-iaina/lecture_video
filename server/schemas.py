"""
Schemas Pydantic pour la validation des donnees API.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== UserChoice Schemas ==========

class ChoiceCreate(BaseModel):
    """Schema pour creer un nouveau choix."""
    choix: str = Field(..., min_length=1, max_length=1, pattern="^[A-G]$")
    video: str = Field(..., min_length=1)
    machine: str = Field(..., min_length=1, max_length=100)


class ChoiceResponse(BaseModel):
    """Schema de reponse pour un choix."""
    id: int
    choix: str
    video: str
    event_time: datetime
    machine: str

    class Config:
        from_attributes = True


class ChoiceListResponse(BaseModel):
    """Schema pour une liste de choix avec pagination."""
    total: int
    items: List[ChoiceResponse]


# ========== Machine Schemas ==========

class MachineCreate(BaseModel):
    """Schema pour enregistrer une nouvelle machine."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = None


class MachineUpdate(BaseModel):
    """Schema pour mettre a jour une machine."""
    description: Optional[str] = None
    location: Optional[str] = None


class MachineResponse(BaseModel):
    """Schema de reponse pour une machine."""
    id: int
    name: str
    description: Optional[str]
    location: Optional[str]
    created_at: datetime
    last_seen: datetime

    class Config:
        from_attributes = True


# ========== Statistics Schemas ==========

class ChoiceStatItem(BaseModel):
    """Statistique pour un choix."""
    choix: str
    count: int
    percentage: float


class MachineStatItem(BaseModel):
    """Statistique pour une machine."""
    machine: str
    total_choices: int
    last_activity: Optional[datetime]


class DailyStatItem(BaseModel):
    """Statistique journaliere."""
    date: str
    count: int


class StatsResponse(BaseModel):
    """Reponse complete des statistiques."""
    total_choices: int
    total_machines: int
    choices_by_button: List[ChoiceStatItem]
    choices_by_machine: List[MachineStatItem]
    daily_activity: List[DailyStatItem]


class HealthResponse(BaseModel):
    """Reponse du health check."""
    status: str
    database: str
    version: str
