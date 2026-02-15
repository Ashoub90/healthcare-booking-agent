# AI Healthcare Booking Agent
Production-Style LLM Agent for Automated Clinic Appointment Scheduling

An AI-powered healthcare booking assistant built with LangChain tool-calling agents, FastAPI, PostgreSQL, and Google Calendar integration.  
This system simulates a real clinic workflow where patients can book, cancel, and manage appointments via natural language chat while the AI autonomously orchestrates tools, memory, and scheduling logic.

Designed as a real clinic prototype with production-style architecture, persistent memory, and real-world integrations.

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

Patient Chat Interface / API  
→ FastAPI /chat Endpoint  
→ AgentService (LangChain Tool-Calling Agent)  
→ Memory Store (PostgreSQL Conversations)  
→ Session State Store (JSONB in PostgreSQL)  
→ Tool Orchestration Layer  
→ Business Services (Patients, Availability, Appointments, Notifications)  
→ External Integrations (Google Calendar, Email SMTP)

This design follows a production-style LLM loop where the agent reasons, calls tools, persists state, and returns structured natural language responses.

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

This was essential for debugging complex agent behaviors such as tool misfires, state desynchronization, and booking workflow issues in a stateful, multi-step LLM system.


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
│   ├── agent/          # LLM agent, memory, session state
│   ├── api/            # FastAPI endpoints (chat, appointments, etc.)
│   ├── services/       # Business logic and integrations
│   ├── tools/          # Agent tool implementations
│   ├── db/             # Models, database, and session config
│   └── main.py         # FastAPI entry point
├── clinic-admin-ui/    # Admin dashboard (React)
├── clinic-patient-chat/# Patient chat interface (React)
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
- patients: Stores patient identity and contact details
- appointments: Appointment records with status and timing
- service_types: Configurable clinic services and durations
- conversations: Persistent chat history for LLM memory
- session_states: JSONB state storage for agent context
- agent_logs: Agent decisions and system actions
- notifications: Email and communication tracking
- blocked_slots: Manually blocked time ranges

This schema enables stateful AI interactions, auditability, and real-world scheduling constraints.

---

## Environment Variables

Create a .env file in the project root:

OPENAI_API_KEY=your_openai_key
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
DATABASE_URL=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILTRAP_USER=your_mailtrap_user
MAILTRAP_PASS=your_mailtrap_pass
MAILTRAP_HOST=your_mailtrap_host
MAILTRAP_PORT=your_mailtrap_port
LANGCHAIN_API_KEY = "lsv2_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT="project_name"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
JWT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

---

## Running with Docker (Recommended)

docker-compose up --build

API will be available at:
http://localhost:8000

Interactive API docs:
http://localhost:8000/docs

---

## Local Development Setup

1. Clone the repository
git clone https://github.com/yourusername/ai-healthcare-booking-agent.git
cd ai-healthcare-booking-agent

2. Install dependencies
pip install -r requirements.txt

3. Run the server
uvicorn app.main:app --reload

---

## Design Decisions

- Deterministic LLM configuration for consistent tool usage
- Two-phase booking confirmation for safe automation
- Tool input sanitization to handle LLM-generated values safely
- Persistent memory instead of in-memory chat storage
- Session-aware tool execution for multi-turn workflows
- Google Calendar + database hybrid availability checking
- Logging layer for observability and debugging
- Production-style layered architecture (API → Agent → Services → DB)

---

## Intended Use

This project is built as a real clinic prototype demonstrating production-style LLM architecture, tool orchestration, persistent memory, and stateful AI agent design for healthcare scheduling workflows.
