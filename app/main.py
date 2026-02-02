from fastapi import FastAPI
from app.api import chat, patients, appointments, availability

app = FastAPI(title="Healthcare Booking Assistant")

app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
app.include_router(availability.router, prefix="/availability", tags=["Availability"])

@app.get("/")
def health_check():
    return {"status": "running"}
