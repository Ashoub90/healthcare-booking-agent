from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date, time

from app.services.patient_service import (
    get_patient_by_phone,
    create_patient
)
from app.services.availability_service import check_availability
from app.services.appointment_service import create_appointment_service, get_appointments_by_patient, cancel_appointment_service
from app.services.notification_service import send_notification_service
from app.services.logging_service import log_agent_action_service

# =========================
# Tool 1: Lookup Patient
# =========================

def lookup_patient_tool(
    phone_number: str,
    db: Session,
    session_state: Dict[str, Any]
) -> Optional[Dict[str, Any]]:

    session_state["phone_number"] = phone_number

    patient = get_patient_by_phone(db, phone_number)

    if not patient:
        session_state["patient_id"] = None
        return None

    session_state["patient_id"] = patient.id

    return {
        "id": patient.id,
        "full_name": patient.full_name,
        "phone_number": patient.phone_number,
        "email": patient.email,
        "is_insured": patient.is_insured,
        "insurance_provider": patient.insurance_provider
    }


# =========================
# Tool 2: Create Patient
# =========================

def create_patient_tool(
    full_name: str,
    phone_number: str,
    email: Optional[str],
    is_insured: Any, # Changed to Any to catch strings from the AI
    insurance_provider: Optional[str],
    db: Session,
    session_state: Dict[str, Any]
) -> str:

    # 1. Validation Guard
    if not phone_number:
        return "Error: Phone number is required to register. Please ask the patient for their phone number."

    # 2. BOOLEAN SANITIZATION LAYER
    # This prevents the (builtins.TypeError) Not a boolean value: 'no' error
    if isinstance(is_insured, str):
        val = is_insured.lower().strip()
        if val in ['yes', 'true', '1', 'y', 'insured']:
            is_insured = True
        elif val in ['no', 'false', '0', 'n', 'uninsured', 'none']:
            is_insured = False
        else:
            # Default to False if the AI sends something ambiguous
            is_insured = False

    try:
        # 3. Database Operation
        patient = create_patient(
            db=db,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            is_insured=is_insured,
            insurance_provider=insurance_provider
        )
        
        # 4. State Persistence
        # We store the ID so the agent doesn't have to ask "Who are you?" again.
        session_state["patient_id"] = patient.id
        session_state["phone_number"] = phone_number
        session_state["full_name"] = full_name
        
        return f"Success: Patient {full_name} registered with ID {patient.id}. You can now proceed to booking."

    except Exception as e:
        db.rollback() 
        return f"System Error: I couldn't save the record because: {str(e)}"
    


# =========================
# Tool 3: Check Availability
# =========================

def check_availability_tool(
    appointment_date: str,
    service_type_id: Any,
    db: Session,
    session_state: Dict[str, Any]
) -> str:
    # 1. AI Auto-Correction (The fix from my last message)
    mapping = {
        "initial consult": 1, "initial consultation": 1,
        "follow-up": 2, "lab review": 3
    }
    
    if isinstance(service_type_id, str):
        clean_id = service_type_id.lower().strip()
        if clean_id in mapping:
            service_type_id = mapping[clean_id]
        elif clean_id.isdigit():
            service_type_id = int(clean_id)

    # 2. Get the slots
    try:
        slots = check_availability(
            appointment_date=appointment_date,
            service_type_id=service_type_id,
            db=db
        )

        if not slots:
            return f"No slots available for {appointment_date}."

        # 3. THE FIX: Convert dictionaries/objects to strings
        # If slots look like [{'start_time': '09:00'}, ...], we do this:
        if isinstance(slots[0], dict):
            slot_strings = [str(s.get('start_time', s)) for s in slots]
        else:
            # If they are objects with a start_time attribute:
            slot_strings = [
                s.start_time.strftime('%H:%M') if hasattr(s, 'start_time') else str(s) 
                for s in slots
            ]

        return f"Available slots for service ID {service_type_id} on {appointment_date}: {', '.join(slot_strings)}"

    except Exception as e:
        return f"System Error while checking availability: {str(e)}"


# =========================
# Tool 4: Create Appointment
# =========================

def create_appointment_tool(
    patient_id: int,
    service_type_id: int,
    appointment_date: date,
    start_time: time,
    db: Session,
    session_state: Dict[str, Any]
) -> str: # Returning str for the agent to read

    if not patient_id:
        return "Error: Cannot book appointment because patient_id is missing. Please identify or register the patient first."

    if session_state.get("appointment_id"):
        return f"The appointment (ID: {session_state['appointment_id']}) is already successfully booked and confirmed. You should now just confirm the details with the patient."
    
    try:
        # 1. Database Execution
        appointment = create_appointment_service(
            db=db,
            patient_id=patient_id,
            service_type_id=service_type_id,
            appointment_date=appointment_date,
            start_time=start_time
        )

        # 2. SUCCESS: Wipe the "Booking Intent" from state
        # This prevents the agent from thinking it still needs to book when the user says "Email"
        session_state["appointment_id"] = appointment.id
        session_state.pop("appointment_date", None)
        session_state.pop("appointment_time", None) # Clear time as well
        session_state.pop("service_type_id", None)  # Clear service type to reset flow

        return (
            f"Success: Appointment confirmed! ID: {appointment.id}, "
            f"Date: {appointment.appointment_date}, "
            f"Time: {appointment.start_time.strftime('%H:%M')} to {appointment.end_time.strftime('%H:%M')}. "
            f"The booking is DONE. Now, strictly ask the patient ONLY if they want confirmation via Email or WhatsApp."
        )

    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        # Determine how to display the time safely
        display_time = start_time
        if hasattr(start_time, 'strftime'):
            display_time = start_time.strftime('%H:%M')

        if "already booked" in error_msg.lower() or "conflict" in error_msg.lower():
            # Now this won't crash even if start_time is a string!
            return f"Notice: This slot ({display_time}) is no longer available. Please ask the user to choose a different time."
            
        return f"System Error: The appointment could not be booked. Reason: {error_msg}"

# =========================
# Tool 5: Send Notification
# =========================

def send_notification_tool(
    appointment_id: int,
    channel: str,
    recipient: str,
    message: str,
    db: Session
) -> Dict[str, Any]:

    notification = send_notification_service(
        appointment_id=appointment_id,
        channel=channel,
        recipient=recipient,
        message=message,
        db=db
    )

    return {
        "notification_id": notification.id,
        "status": notification.status
    }


def get_patient_appointments_tool(
    patient_id: int,
    db: Session
) -> str:
    """Retrieves all upcoming appointments for a specific patient."""
    
    if not patient_id:
        return "Error: I don't have a patient ID. Please identify the patient first."

    try:
        
        appointments = get_appointments_by_patient(db, patient_id)

        if not appointments:
            return "The patient has no appointments scheduled."

        # Format the list into a readable string for the AI
        report = "Here are the patient's upcoming appointments:\n"
        for appt in appointments:
            report += f"- ID: {appt.id} | Date: {appt.appointment_date} | Time: {appt.start_time.strftime('%H:%M')} | Status: {appt.status}\n"
        
        return report

    except Exception as e:
        return f"System Error: Could not retrieve appointments. {str(e)}"    


def cancel_appointment_tool(
    appointment_id: int,
    db: Session
) -> str:
    """Cancels an existing appointment by its ID."""
    try:
        cancel_appointment_service(db, appointment_id)
        return f"Success: Appointment {appointment_id} has been cancelled."
    except Exception as e:
        db.rollback()
        return f"Error: Could not cancel appointment. {str(e)}"        