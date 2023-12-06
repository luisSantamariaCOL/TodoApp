import models

from database import engine
from routers import auth, todos
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette import status
from starlette.staticfiles import StaticFiles

app = FastAPI()

# Redirect root path to "/docs"
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)
