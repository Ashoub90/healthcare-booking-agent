# AI Healthcare Booking Agent
Production-Style LLM Agent for Automated Clinic Appointment Scheduling

An AI-powered healthcare booking assistant built with LangChain tool-calling agents, FastAPI, PostgreSQL, and Google Calendar integration.  
This system simulates a real clinic workflow where patients can book, cancel, and manage appointments via natural language chat while the AI autonomously orchestrates tools, memory, and scheduling logic.

Designed as a real clinic prototype with production-style architecture, persistent memory, and real-world integrations.

---

## 🎙️ Voice Interface (Companion Project)

This backend is paired with a real-time voice AI interface:

Voice Agent (LiveKit + STT + TTS):  
https://github.com/Ashoub90/voice-agent

The voice-agent project enables:
- Real-time voice conversations (Arabic / English)
- Speech-to-text (Deepgram)
- Text-to-speech (ElevenLabs)
- LiveKit-based streaming communication
- Agent dispatching based on selected language

Together, both projects form a complete conversational AI system:
- This repo = brain (logic, tools, memory, scheduling)
- Voice-agent = voice (real-time interaction layer)

---

## Overview

This project implements a stateful, tool-augmented AI agent that handles end-to-end appointment scheduling for a medical clinic.  
Instead of acting as a simple chatbot, the system uses a LangChain tool-calling agent connected to real business logic, a relational database, and external services such as Google Calendar and email notifications.

The agent maintains persistent conversation memory, session state, and executes structured tools to perform real actions such as patient registration, availability checks, appointment booking, and notifications.

---

## Core Features

### Tool-Calling LLM Agent
- LangChain create_tool_calling_agent architecture
- Deterministic reasoning (temperature = 0) for reliability
- Multi-step autonomous booking workflow
- Two-phase confirmation before appointment creation
- Natural language date and time handling
- Dynamic tool injection per session

### Persistent Memory and Session State
- PostgreSQL-backed conversation memory
- JSONB session state stored per session_id
- Context-aware multi-turn conversations
- Token-trimmed chat history for context efficiency
- Database upsert for session continuity

### Real Scheduling Logic (Not Mocked)
- Dynamic availability generation based on business hours
- Lead-time enforcement for bookings
- Conflict detection with existing appointments
- Blocked slots and clinic schedule awareness
- Google Calendar busy-slot synchronization
- Graceful fallback if external calendar fails

### Real-World Integrations
- Google Calendar API (event creation, deletion, busy slot checks)
- Email notifications via Mailtrap (SMTP)
- PostgreSQL for persistent storage
- Dockerized multi-service deployment
- OAuth2 protected admin endpoints

### Clinic Workflow Automation
The AI agent can:
- Identify existing patients via phone number
- Register new patients
- Check real appointment availability
- Book appointments with confirmation logic
- Cancel appointments
- Retrieve patient appointment history
- Send confirmation notifications (Email)
- Log agent actions for observability and auditing

---

## System Architecture

Patient Chat Interface / Voice Agent  
→ FastAPI /chat Endpoint  
→ AgentService (LangChain Tool-Calling Agent)  
→ Memory Store (PostgreSQL Conversations)  
→ Session State Store (JSONB in PostgreSQL)  
→ Tool Orchestration Layer  
→ Business Services (Patients, Availability, Appointments, Notifications)  
→ External Integrations (Google Calendar, Email SMTP)

---

## Agent Workflow

1. User sends a message to the /chat endpoint with a session_id  
2. System loads:
   - Conversation memory from PostgreSQL
   - Session state (patient_id, booking context, etc.)
3. Chat history is trimmed to control token usage
4. The LLM agent reasons using:
   - System prompt (clinic rules and workflow)
   - Session state
   - Chat history
5. The agent dynamically calls tools such as:
   - lookup_patient
   - create_patient
   - check_availability
   - create_appointment
   - send_notification
   - cancel_appointment
6. Tool results update the database and session state
7. Memory and state are persisted back to PostgreSQL
8. A final natural language reply is returned to the user

Note: The /chat endpoint returns full responses (non-streaming) after tool execution.

---

## Observability (LangSmith)

This project uses LangSmith to trace and debug the LangChain agent’s reasoning and tool execution in real time.

Each chat request is logged with:
- Agent decision steps
- Tool calls and inputs/outputs
- Prompt context and session state
- Errors and retries

---

## Tech Stack

### AI and LLM
- OpenAI (GPT-4o-mini)
- LangChain (Tool Calling Agents)
- Prompt Engineering for structured workflows

### Backend
- FastAPI
- SQLAlchemy ORM
- Pydantic
- Python 3.11

### Database and State Management
- PostgreSQL
- JSONB session state storage
- Persistent conversation logs

### Integrations
- Google Calendar API
- Mailtrap SMTP (Email Notifications)

### DevOps and Deployment
- Docker
- Docker Compose
- Uvicorn ASGI Server

---

## Project Structure

ai-healthcare-booking-agent/
├── app/
│   ├── agent/
│   ├── api/
│   ├── services/
│   ├── tools/
│   ├── db/
│   └── main.py
├── clinic-admin-ui/
├── clinic-patient-chat/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

---

## API Endpoints

### Public Endpoints
- POST /chat — Main AI booking interaction
- GET /availability — Check available time slots
- GET /service-types — List available clinic services
- GET /business-hours — Retrieve clinic schedule

### Protected Endpoints (OAuth2 Bearer Token)
- /patients
- /appointments
- /logs

Demo Credentials:
- Username: admin
- Password: password123

---

## Chat API Example

Request:
{
  "session_id": "user_123",
  "message": "I want to book an appointment tomorrow"
}

Response:
{
  "reply": "Sure, what time would you like to come in?",
  "data": {}
}

---

## Database Design

Key tables:
- patients
- appointments
- service_types
- conversations
- session_states
- agent_logs
- notifications
- blocked_slots

---

## Environment Variables

Create a .env file:

OPENAI_API_KEY=your_openai_key
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
DATABASE_URL=...
MAILTRAP_USER=...
MAILTRAP_PASS=...
MAILTRAP_HOST=...
MAILTRAP_PORT=...
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=...
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
JWT_SECRET=...

---

## Running with Docker

docker-compose up --build

API:
http://localhost:8000

Docs:
http://localhost:8000/docs

---

## Local Development

git clone https://github.com/Ashoub90/ai-healthcare-booking-agent.git
cd ai-healthcare-booking-agent
pip install -r requirements.txt
uvicorn app.main:app --reload

---

## Design Decisions

- Deterministic LLM for reliability
- Two-phase confirmation for safe booking
- Persistent memory instead of in-memory chat
- Session-aware workflows
- Hybrid availability (DB + Google Calendar)
- Full observability via logging and LangSmith
- Production-style layered architecture

---

## Intended Use

This project demonstrates a production-style AI agent capable of real-world healthcare scheduling, combining LLM reasoning, tool orchestration, persistent memory, and external integrations.

It is designed to be used alongside the voice-agent project to enable fully conversational (voice + text) booking experiences.