from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def incidents_page(request: Request, db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    return templates.TemplateResponse(
        request,
        "incidents/list.html",
        {"incidents": incidents},
    )


@router.get("/api", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()


@router.get("/api/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/api", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.patch("/api/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    return incident


@router.delete("/api/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    db.delete(incident)
    db.commit()
