from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from backend.app.extensions import get_db
from backend.api.models.appointment import Appointment
from backend.auth.routes import get_current_user
from backend.auth.models import User

appointments_router = APIRouter()

class AppointmentCreateSchema(BaseModel):
    therapist_name: str
    date_time: str

class AppointmentSchema(BaseModel):
    id: int
    therapist_name: str
    date_time: str
    status: str

    class Config:
        from_attributes = True

@appointments_router.get("/", response_model=List[AppointmentSchema])
def get_appointments(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Retrieve user's appointments
    return db.query(Appointment).filter(Appointment.user_id == current_user.id).all()

@appointments_router.post("/", response_model=AppointmentSchema, status_code=status.HTTP_201_CREATED)
def create_appointment(
    data: AppointmentCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = Appointment(
        user_id=current_user.id,
        therapist_name=data.therapist_name,
        date_time=data.date_time,
        status="Scheduled"
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    # Trigger SMS/Email confirmations (mocked)
    from backend.services.sms import send_sms
    from backend.services.email import send_email
    send_sms(f"Hi {current_user.username}, your appointment with {data.therapist_name} is confirmed for {data.date_time}.")
    send_email(current_user.email, "Appointment Confirmed", f"Appointment confirmed with {data.therapist_name} at {data.date_time}.")
    
    return appointment
