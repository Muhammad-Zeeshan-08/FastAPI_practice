from fastapi import FastAPI, HTTPException, status
import uvicorn
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
# @()

# # WRONG: valid for normal var in python. but pydantic model require type annotations for each field individually to validate the incoming data correctly.
# class CreateTicketRequest(BaseModel):
#     customer_name, email, subject, description, category: str       #here actually just category is str
#     priority: int

# *************** REQUEST MODELS **********************
class CreateTicketRequest(BaseModel):
    name: str
    email: str
    subject: str
    description: str
    # priority: int
    # category: str
    # status: str

class UpdateTicketRequest(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None

# *************** RESPONSE MODEL **********************
class TicketResponse(BaseModel): # describes the shape of ONE item
    id: int
    name: str
    email: str
    subject: str
    description: str
    priority: int
    status: str
    # category: str

# *************** LOGIC **********************
ticket_log = []

# here we take inp from client as per CreateTicketRequest model & server add 3 more data so that it can b/c TicketResponse
# Invalid request: 422 Unprocessable Entity.    FastAPI/Pydantic provides auto_validation.
@app.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def ticket_create(model: CreateTicketRequest):
    new_ticket = TicketResponse(
        id=len(ticket_log) + 1,
        name=model.name,
        email=model.email,
        subject=model.subject,
        description=model.description,
        priority=1,
        status="open"
    )
    ticket_log.append(new_ticket)
    return new_ticket

@app.get("/tickets",response_model=list[TicketResponse])
def get_all_tickets():
    # if len(ticket_log) == 0:      # wrong b/c it must follow the TicketResponse format
    #     return{
    #         "message": "There is currently no Tickets data"
    #     }

    # if len(ticket_log) == 0:      # correct but not a standord approach thats why just return enough which will sent [] in this scenario
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND, 
    #         detail="There is currently no Tickets data"
    #     )
    return ticket_log

@app.get("/tickets/{ticket_id}",response_model=TicketResponse)
def get_ticket(ticket_id: int):
    for ticket in ticket_log:
        if ticket.id == ticket_id: # thats the pydanctic instance benefit over dict. b/c here we can access key/var via .
            return ticket
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ticket not found"
    )

@app.patch("/tickets/{ticket_id}",response_model=TicketResponse)
def ticket_partial_update(ticket_id: int,model: UpdateTicketRequest):
    for ticket in ticket_log:
        if ticket.id == ticket_id:
            updates = model.model_dump(exclude_unset=True) # result in dict form
        for field, value in updates.items():
                setattr(ticket, field, value)
                # updated/merge_item_copy = ticket.model_copy(update=updates) 

        return ticket # updated/merge_item_copy. by this the orginal ticket will remain same

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