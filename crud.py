# for better understanding:
# todo_list       → the global Python list
# todo            → parameter containing ONE Todo object
# Todo            → Pydantic class/model

# todo.id → Id of Todo object, which we are providing in POST body.
# todos_no → value coming from URL, e.g. /todos/500.

# NOTE:
# If there is +1 data with the same index. Then for all the operations[get, put, del] behavior will be same:
# Find the FIRST item satisfying the condition, then immediately stop.

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status
import uvicorn

# todo = [] talking about this one
todo_list = []

class Todo(BaseModel):
    id: int
    title: str
    complete_status: bool

app = FastAPI()
@app.post("/todos")
def create_todo(todo: Todo):
    todo_list.append(todo)      # when i write, it assume para todo not the todo var at line5: todo.append(todo) 
    return{
        "msg": "Todo Created",
        "data": todo            # todo to return that specific data
    }

@app.get("/todos")
def get_all_todo():
    return todo_list            # todo_list to return entire data

@app.get("/todos/{todos_no}")
def get_todo(todos_no:int):
    for todo in todo_list:
        if todo.id == todos_no:
            return { "msg": f"Todo{todos_no} provided ", "data": todo}
    return{
            "Error": f"That Todo {todos_no} not Found "
        }

@app.put("/todos/{todos_no}")
def update_todo(todos_no: int, updated_todo: Todo):
    for no, todo in enumerate(todo_list):
        if todo.id == todos_no:
            todo_list[no] = updated_todo
            return {"msg": "Todo updated", "data": updated_todo}
    return{"That Todo-number doesn't exist"}
    
@app.delete("/todos/{todos_no}")
def delete_todo(todos_no: int):
    for no, todo in enumerate(todo_list):
        if todo.id == todos_no:
                todo_list.pop(no)
                return {"msg": "Todo updated after deletion", "current_data": todo_list}
    return{f"This Todo {no} doesn't exist"}                

if __name__ == "__main__":
    uvicorn.run("crud:app", reload=True)    # crud:app  means telling the Uvicorn to run the app of Crud.py file

# @()
