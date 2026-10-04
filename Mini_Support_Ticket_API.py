from fastapi import FastAPI, HTTPException, status
import uvicorn
from pydantic import BaseModel
import time

app = FastAPI()
# @()

# # WRONG: valid for normal var in python. but pydantic model require type annotations for each field individually to validate the incoming data correctly.
# class CreateTicketRequest(BaseModel):
#     customer_name, email, subject, description, category: str       #here actually just category is str
#     priority: int

class CreateTicketRequest(BaseModel):
    customer_name: str
    email: str
    subject: str
    description:str
    priority: int
    category: str
    situation: str

class UpdateTicketRequest(BaseModel):
    subject: str
    description: str
    priority: int
    situation: str

class TicketResponse(BaseModel):
    customer_name: str
    email: str
    subject: str
    description:str
    category: str
    situation: str

ticket_log = []

@app.post("/tickets")
def ticket_create(model: CreateTicketRequest):
    ticket_log.append(model)
    return{
        "status": status.HTTP_201_CREATED,
        "detail": f"The ticket data has been in the system" 
    }

@app.get("/tickets", response_model= TicketResponse)
def get_all_tickets():
    if len(ticket_log) == 0:
        return{
            "message": "There is currently no Tickets data"
        }
    return ticket_log

@app.get("/tickets/{ticket_id}", response_model= TicketResponse)
def get_ticket(ticket_id:int):
    if len(ticket_log) == 0:
        return{
            "error_message": "There is currently no Tickets data in the system"
        }
    elif ticket_id > len(ticket_log):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,       
            detail= "There is no such Ticket number exist in the system"
        )
    else:
        for i, content in enumerate(ticket_log):
            number = i+1
            if ticket_id == number:
                return{
                    "message": f"The data for Ticket number {number} :",
                    "data": content
                }

@app.patch("/tickets/{ticket_id}")
def ticket_partial_update(ticket_id:int, model: UpdateTicketRequest):
    if len(ticket_log) == 0:
        return{
            "error_message": "There is currently no Tickets data in the system"
        }
    elif ticket_id > len(ticket_log):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,       
            detail= "There is no such Ticket number exist in the system"
        )
    else:
        for i, content in enumerate(ticket_log):
            if ticket_id == i:
                return{
                    "message": f"The ticket data is UPDATED for Ticket number {i} :",
                    content.subject : model.subject,
                    content.description : model.description,
                    content.situation : model.situation,
                    content.priority : model.priority,
                }
    
@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):
    if len(ticket_log) == 0:
        return{
            "error_message": "There is currently no Tickets data in the system"
        }
    elif ticket_id > len(ticket_log):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,       
            detail= "There is no such Ticket number exist in the system"
        )
    else:
        for i, content in enumerate(ticket_log):
            if ticket_id == i:
                return{
                    "message": f"The Ticket number {i} data is DELETED from the system :",
                    "ticket_log_updated": ticket_log.pop(content)
                }

if __name__ == "__main__":
    uvicorn.run("Mini_Support_Ticket_API:app", reload=True)

# def get_user(user_id:int):
#     if user_id != 1: 
#         raise HTTPException(
#             status_code= 404,       # or status_code= status.HTTP_404_NOT_FOUND,
#             detail="User Not Found"
#         )
#     return{
#         "id":1,
#         "name": "Mohit"
#     }
