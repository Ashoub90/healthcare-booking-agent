from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


# 1️⃣ patients
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True)
    is_insured = Column(Boolean, default=False)
    insurance_provider = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="patient")
    logs = relationship("AgentLog", back_populates="patient")


# 2️⃣ service_types
class ServiceType(Base):
    __tablename__ = "service_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    requires_confirmation = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    appointments = relationship("Appointment", back_populates="service_type")


# 3️⃣ business_hours
class BusinessHour(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False)
    open_time = Column(Time, nullable=True)
    close_time = Column(Time, nullable=True)
    is_closed = Column(Boolean, default=False)


# 4️⃣ appointments
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    service_type_id = Column(Integer, ForeignKey("service_types.id"), nullable=False)

    appointment_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    status = Column(String, default="pending")  
    # pending | confirmed | cancelled

    external_calendar_id = Column(String, nullable=True)
    sync_status = Column(String, default="not_synced")
    # not_synced | synced | failed

    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="appointments")
    service_type = relationship("ServiceType", back_populates="appointments")
    notifications = relationship("Notification", back_populates="appointment")



# 5️⃣ agent_logs
class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)

    user_message = Column(String, nullable=False)
    agent_action = Column(String, nullable=False)
    # check_availability | book_appointment | cancel_appointment | suggest_time

    system_decision = Column(String, nullable=False)
    # booked | suggested_alternative | failed | cancelled

    confidence_score = Column(Float, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="logs")



# 6️⃣ notifications
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    channel = Column(String, nullable=False)  # email / whatsapp
    recipient = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="notifications")
