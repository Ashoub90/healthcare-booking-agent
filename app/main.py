from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.api import patients, appointments, availability, service_types, business_hours, chat, logs
from app.db.session import create_tables
from app.core.security import create_access_token

app = FastAPI(title="Healthcare Booking Assistant")

# This tells FastAPI where to look for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

create_tables()

# PROTECTED ROUTES (Require Token)
app.include_router(
    patients.router, 
    prefix="/patients", 
    tags=["Patients"], 
    dependencies=[Depends(oauth2_scheme)]
)
app.include_router(
    appointments.router, 
    prefix="/appointments", 
    tags=["Appointments"], 
    dependencies=[Depends(oauth2_scheme)]
)
app.include_router(
    logs.router, 
    prefix="/logs", 
    tags=["Logs"], 
    dependencies=[Depends(oauth2_scheme)]
)

# PUBLIC ROUTES (No Token Needed)
app.include_router(service_types.router, prefix="/service-types", tags=["Service Types"])
app.include_router(business_hours.router, prefix="/business-hours", tags=["Business Hours"])
app.include_router(availability.router, prefix="/availability", tags=["Availability"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # This is the generic user for your LinkedIn recruiters
    if form_data.username != "admin" or form_data.password != "password123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def health_check():
    return {"status": "running"}