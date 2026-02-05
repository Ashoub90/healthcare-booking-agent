from fastapi import FastAPI
from app.api import patients, appointments, availability, service_types, business_hours, chat
from app.db.session import create_tables

app = FastAPI(title="Healthcare Booking Assistant")

create_tables()

app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(service_types.router, prefix="/service-types", tags=["Service Types"])
app.include_router(business_hours.router, prefix="/business-hours", tags=["Business Hours"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(availability.router, prefix="/availability", tags=["Availability"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])



@app.get("/")
def health_check():
    return {"status": "running"}
