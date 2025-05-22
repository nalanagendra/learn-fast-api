from fastapi import FastAPI
from database import engine
import models
from routers import auth, todos, admin, users

app = FastAPI()

# only be ran when db does not exist
# Everytime create change in model delete and execute again
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
