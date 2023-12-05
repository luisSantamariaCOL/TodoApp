import sys
sys.path.append("..")

import models
from fastapi import (
    Depends, 
    HTTPException, 
    APIRouter, 
    Request, 
    Form
    )

from starlette.status import (HTTP_302_FOUND)

from typing import Optional
from models import Todos
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_exception
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    
    todos = db.query(Todos).filter(Todos.owner_id == 1).all()
    
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, 
                      title: str = Form(...),
                      description: str = Form(...), 
                      priority: int = Form(...),
                      db: Session = Depends(get_db)):
    todo_model = Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = 1 # tmp
    
    db.add(todo_model)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo})

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, 
                           title: str = Form(...), 
                           description: str = Form(...),
                           priority: int = Form(...),
                           db: Session = Depends(get_db)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    
    db.add(todo_model)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=HTTP_302_FOUND)

@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int,
                      db: Session = Depends(get_db)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == 1).first()
    
    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=HTTP_302_FOUND)
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=HTTP_302_FOUND)

@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, 
                        db: Session = Depends(get_db)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    
    todo.complete = not todo.complete
    
    db.add(todo)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=HTTP_302_FOUND)