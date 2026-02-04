"""
API FastAPI pour la gestion des donnees video analytics.

Ce serveur centralise les donnees de toutes les bornes video.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from database import get_db, init_db, engine
from models import Base, UserChoice, Machine
from schemas import (
    ChoiceCreate, ChoiceResponse, ChoiceListResponse,
    MachineCreate, MachineUpdate, MachineResponse,
    StatsResponse, ChoiceStatItem, MachineStatItem, DailyStatItem,
    HealthResponse
)

# Version de l'API
API_VERSION = "1.0.0"

# Creation de l'application FastAPI
app = FastAPI(
    title="Video Analytics API",
    description="API pour centraliser les donnees des bornes video interactives",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour permettre les appels depuis les bornes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialise la base de donnees au demarrage."""
    Base.metadata.create_all(bind=engine)


# ========== Health Check ==========

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Verifie l'etat du serveur et de la base de donnees."""
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok",
        database=db_status,
        version=API_VERSION
    )


# ========== Choices Endpoints ==========

@app.post("/choices", response_model=ChoiceResponse, status_code=201, tags=["Choices"])
def create_choice(choice: ChoiceCreate, db: Session = Depends(get_db)):
    """
    Enregistre un nouveau choix utilisateur.

    Cette endpoint est appelee par les bornes a chaque pression de bouton.
    """
    # Mettre a jour last_seen de la machine
    machine = db.query(Machine).filter(Machine.name == choice.machine).first()
    if machine:
        machine.last_seen = datetime.utcnow()
    else:
        # Auto-enregistrement de la machine si inconnue
        machine = Machine(name=choice.machine)
        db.add(machine)

    # Creer le choix
    db_choice = UserChoice(
        choix=choice.choix.upper(),
        video=choice.video,
        machine=choice.machine
    )
    db.add(db_choice)
    db.commit()
    db.refresh(db_choice)

    return db_choice


@app.get("/choices", response_model=ChoiceListResponse, tags=["Choices"])
def list_choices(
    machine: Optional[str] = Query(None, description="Filtrer par machine"),
    choix: Optional[str] = Query(None, description="Filtrer par bouton (A-G)"),
    days: int = Query(7, ge=1, le=365, description="Nombre de jours"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Liste les choix avec filtres et pagination."""
    query = db.query(UserChoice)

    # Filtres
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = query.filter(UserChoice.event_time >= cutoff)

    if machine:
        query = query.filter(UserChoice.machine == machine)
    if choix:
        query = query.filter(UserChoice.choix == choix.upper())

    # Total et pagination
    total = query.count()
    items = query.order_by(desc(UserChoice.event_time)).offset(offset).limit(limit).all()

    return ChoiceListResponse(total=total, items=items)


@app.get("/choices/{choice_id}", response_model=ChoiceResponse, tags=["Choices"])
def get_choice(choice_id: int, db: Session = Depends(get_db)):
    """Recupere un choix par son ID."""
    choice = db.query(UserChoice).filter(UserChoice.id == choice_id).first()
    if not choice:
        raise HTTPException(status_code=404, detail="Choix non trouve")
    return choice


@app.delete("/choices/{choice_id}", status_code=204, tags=["Choices"])
def delete_choice(choice_id: int, db: Session = Depends(get_db)):
    """Supprime un choix par son ID."""
    choice = db.query(UserChoice).filter(UserChoice.id == choice_id).first()
    if not choice:
        raise HTTPException(status_code=404, detail="Choix non trouve")
    db.delete(choice)
    db.commit()


# ========== Machines Endpoints ==========

@app.post("/machines", response_model=MachineResponse, status_code=201, tags=["Machines"])
def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):
    """Enregistre une nouvelle machine."""
    existing = db.query(Machine).filter(Machine.name == machine.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Machine deja enregistree")

    db_machine = Machine(**machine.model_dump())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)

    return db_machine


@app.get("/machines", response_model=list[MachineResponse], tags=["Machines"])
def list_machines(db: Session = Depends(get_db)):
    """Liste toutes les machines enregistrees."""
    return db.query(Machine).order_by(Machine.name).all()


@app.get("/machines/{machine_name}", response_model=MachineResponse, tags=["Machines"])
def get_machine(machine_name: str, db: Session = Depends(get_db)):
    """Recupere une machine par son nom."""
    machine = db.query(Machine).filter(Machine.name == machine_name).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine non trouvee")
    return machine


@app.put("/machines/{machine_name}", response_model=MachineResponse, tags=["Machines"])
def update_machine(
    machine_name: str,
    update: MachineUpdate,
    db: Session = Depends(get_db)
):
    """Met a jour une machine."""
    machine = db.query(Machine).filter(Machine.name == machine_name).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine non trouvee")

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(machine, key, value)

    db.commit()
    db.refresh(machine)
    return machine


@app.delete("/machines/{machine_name}", status_code=204, tags=["Machines"])
def delete_machine(machine_name: str, db: Session = Depends(get_db)):
    """Supprime une machine."""
    machine = db.query(Machine).filter(Machine.name == machine_name).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine non trouvee")
    db.delete(machine)
    db.commit()


# ========== Statistics Endpoints ==========

@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
def get_stats(
    machine: Optional[str] = Query(None, description="Filtrer par machine"),
    days: int = Query(7, ge=1, le=365, description="Periode en jours"),
    db: Session = Depends(get_db)
):
    """
    Recupere les statistiques d'utilisation.

    Retourne:
    - Total des choix
    - Repartition par bouton
    - Repartition par machine
    - Activite journaliere
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Base query
    base_query = db.query(UserChoice).filter(UserChoice.event_time >= cutoff)
    if machine:
        base_query = base_query.filter(UserChoice.machine == machine)

    # Total choices
    total_choices = base_query.count()

    # Total machines
    total_machines = db.query(Machine).count()

    # Choices by button
    button_stats = (
        base_query
        .with_entities(UserChoice.choix, func.count(UserChoice.id))
        .group_by(UserChoice.choix)
        .order_by(desc(func.count(UserChoice.id)))
        .all()
    )

    choices_by_button = [
        ChoiceStatItem(
            choix=row[0],
            count=row[1],
            percentage=round(row[1] / total_choices * 100, 1) if total_choices > 0 else 0
        )
        for row in button_stats
    ]

    # Choices by machine
    machine_stats = (
        db.query(UserChoice)
        .filter(UserChoice.event_time >= cutoff)
        .with_entities(
            UserChoice.machine,
            func.count(UserChoice.id),
            func.max(UserChoice.event_time)
        )
        .group_by(UserChoice.machine)
        .order_by(desc(func.count(UserChoice.id)))
        .all()
    )

    choices_by_machine = [
        MachineStatItem(
            machine=row[0],
            total_choices=row[1],
            last_activity=row[2]
        )
        for row in machine_stats
    ]

    # Daily activity
    daily_stats = (
        base_query
        .with_entities(
            func.date(UserChoice.event_time).label("date"),
            func.count(UserChoice.id)
        )
        .group_by(func.date(UserChoice.event_time))
        .order_by(func.date(UserChoice.event_time))
        .all()
    )

    daily_activity = [
        DailyStatItem(date=str(row[0]), count=row[1])
        for row in daily_stats
    ]

    return StatsResponse(
        total_choices=total_choices,
        total_machines=total_machines,
        choices_by_button=choices_by_button,
        choices_by_machine=choices_by_machine,
        daily_activity=daily_activity
    )


@app.get("/stats/live", tags=["Statistics"])
def get_live_stats(db: Session = Depends(get_db)):
    """
    Statistiques en temps reel (derniere heure).

    Utile pour un dashboard live.
    """
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    recent_choices = (
        db.query(UserChoice)
        .filter(UserChoice.event_time >= one_hour_ago)
        .order_by(desc(UserChoice.event_time))
        .limit(20)
        .all()
    )

    active_machines = (
        db.query(Machine)
        .filter(Machine.last_seen >= one_hour_ago)
        .all()
    )

    return {
        "recent_choices": [
            {
                "choix": c.choix,
                "machine": c.machine,
                "time": c.event_time.isoformat()
            }
            for c in recent_choices
        ],
        "active_machines": [m.name for m in active_machines],
        "choices_last_hour": len(recent_choices)
    }


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
