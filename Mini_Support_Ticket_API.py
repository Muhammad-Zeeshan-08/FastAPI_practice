# @()
import logging
import time
import uuid
import uvicorn
from itertools import count # this will give unique id to every ticket until the app is running

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing import Optional, Literal, Annotated
# For much better & strong Request validation, we use: Pydantic Field, EmailStr, StringConstraints & Literal

# Setup Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

CleanString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

# # WRONG: valid for normal var in python. but pydantic model require type annotations[simply means dt] for each field individually to validate the incoming data correctly.
# class CreateTicketRequest(BaseModel):
#     customer_name, email, subject, description, category: str       #here actually just category is str
#     priority: int

# *************** REQUEST MODELS **********************
# Below one is Modern syntax: L.H.S is just type hint & = val [eg; = None] means telling default value. if no r.h.s then user need to provide value 
class CreateTicketRequest(BaseModel):
    name: CleanString = Field(max_length=50)
    email: EmailStr
    subject: CleanString = Field(max_length=150)
    description: CleanString= Field(max_length=2000)
    priority: Literal[1, 2, 3] = 1

class UpdateTicketRequest(BaseModel): 
    subject: CleanString | None = Field(default=None, max_length=150)
    description: CleanString | None = Field(default=None, max_length=2000)
    priority: Literal[1, 2, 3] | None = None
    status: Literal["open", "in_progress", "resolved", "closed"] | None = None

# *************** RESPONSE MODEL **********************
class TicketResponse(BaseModel): # describes the shape of ONE item
    id: int
    name: str
    email: str
    subject: str
    description: str
    priority: int
    status: str

# *************** CUSTOM RESPONSE / WRAPPER **********************
class TicketEnvelope(BaseModel):
    success: bool
    message: str
    data: TicketResponse

class TicketListEnvelope(BaseModel):
    success: bool
    message: str
    data: list[TicketResponse]

# *************** Custom Exception **********************
class TicketAlreadyClosedException(Exception):
    pass

# Global exception handler
@app.exception_handler(TicketAlreadyClosedException)
async def closed_ticket_handler(request: Request,exc: TicketAlreadyClosedException): # HTTP request object,  exception/error instance/object
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "message": "Closed tickets cannot be updated",
            "data": None
        }
    )

# Validation error handler
# Professional way, exc.errors() tells the frontend exactly which field (like password or email) failed validation and why.
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"] if loc != "body"),
            "issue": error["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Request validation failed",
            "data": formatted_errors  # Now providing field-level details!
        }
    )

# *************** Standardize HTTP Exception**********************
@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request,exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "data": None
        },
        headers=exc.headers # HTTP Header Preservation {Protects standard HTTP headers (like security/auth headers)}
    )

# *************** LOGIC **********************
ticket_log = []
ticket_id_counter = count(1)
allowed_transitions = {
    "open": ["in_progress"], "in_progress": ["resolved"], "resolved": ["closed"], "closed": []
}

# *************** MIDDLEWARE**********************

# Middleware Definition (The Guard)
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    # Tracking the Incoming Request
    request_id = str(uuid.uuid4()) # will always create Unique and random id
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Request failed | request_id=%s | method=%s | path=%s",
            request_id,
            request.method,
            request.url.path
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000 # how many ms it took your backend to process everything.
    response.headers["X-Request-ID"] = request_id # if app crash, to track issue via that unique id. it work as label on package
    
    # Logging the Success & Sending it Back
    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms
    )

    return response

# *************** HTTP METHODS / ENDPOINTS **********************
# here we take inp from client as per CreateTicketRequest model & server add 3 more data so that it can b/c TicketResponse
# Invalid request: 422 Unprocessable Entity.    FastAPI/Pydantic provides auto_validation.
@app.post("/tickets", response_model=TicketEnvelope, status_code=status.HTTP_201_CREATED)
def ticket_create(model: CreateTicketRequest):
    new_ticket = TicketResponse(
        id=next(ticket_id_counter), # len(ticket_log) + 1 this logic will cause duplication issue if any ticket is deleted
        name=model.name,
        email=model.email,
        subject=model.subject,
        description=model.description,
        priority=model.priority,
        status="open"
    )
    ticket_log.append(new_ticket)
    return {
        "success": True,
        "message": "Ticket created successfully",
        "data": new_ticket
    }

@app.get("/tickets", response_model=TicketListEnvelope, status_code=status.HTTP_200_OK)
def get_all_tickets():
    return {
        "success": True,
        "message": "Tickets retrieved successfully",
        "data": ticket_log
    }

@app.get("/tickets/{ticket_id}",response_model=TicketEnvelope, status_code=status.HTTP_200_OK)
def get_ticket(ticket_id: int):
    for ticket in ticket_log:
        if ticket.id == ticket_id: # thats the pydanctic instance benefit over dict. b/c here we can access key/var via .
                return {
                    "success": True,
                    "message": "Ticket retrieved successfully",
                    "data": ticket
                }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ticket not found"
        # "success": false,
        # "message": "Ticket not found",
        # "data": null
    )

@app.patch("/tickets/{ticket_id}", response_model=TicketEnvelope, status_code=status.HTTP_200_OK)
def ticket_partial_update(ticket_id: int,model: UpdateTicketRequest):
    for ticket in ticket_log:
        if ticket.id == ticket_id:
            # Our Transition Rules:
            # Rule 1: Closed tickets cannot be updated
            if ticket.status == "closed":
                # M1[via HTTP Exception]
                # raise HTTPException(
                #     status_code=status.HTTP_409_CONFLICT,
                #     detail="Closed tickets cannot be updated"
                # )
                # M2[via Custom Exception]
                raise TicketAlreadyClosedException()
            updates = model.model_dump(exclude_unset=True) # result in dict form
            # Rule 2: Reject an empty PATCH request [it means if update is empty dic [ {} ] which means nothing is provided to update]
            if not updates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one field must be provided"
                )
            # Rule 3: Reject explicit null values
            if any(value is None for value in updates.values()): # {"subject": null} to handle such case as, subj must be str. so to prevent it to accept null etc
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Fields cannot be null"
                )
            # Rule 4: Validate status transitions only + when the client provides the status field only
            if "status" in updates:
                requested_status = updates["status"]
                current_status = ticket.status
                allowed_next_statuses = allowed_transitions[current_status]
                
                if requested_status not in allowed_next_statuses:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(f"Invalid status transition: " f"{current_status} -> {requested_status}")
                    )
            # Rule 5: Apply updates after all checks pass
            for field, value in updates.items():
                setattr(ticket, field, value)
                # updated/merge_item_copy = ticket.model_copy(update=updates) . updated/merge_item_copy. by this the orginal ticket will remain same
            return {
                "success": True,
                "message": "Ticket updated successfully",
                "data": ticket
            } 
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ticket not found"
    )

@app.delete("/tickets/{ticket_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int):
    for i, ticket in enumerate(ticket_log):
        if ticket.id == ticket_id:
            ticket_log.pop(i)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ticket not found"
    )

# *************** SERVER EXECUTION **********************
if __name__ == "__main__":
    uvicorn.run("Mini_Support_Ticket_API:app", reload=True)