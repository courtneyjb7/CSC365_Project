from fastapi import FastAPI
from src.api import trainers, pkg_util, classes, dogs

description = """
Dog Training and Boarding company
"""
tags_metadata = [
    {
        "name": "classes",
        "description": "Access and update information on classes available.",
    },
    {
        "name": "trainers",
        "description": "Access information on trainers.",
    },
    {
        "name": "dogs",
        "description": "Access and update information on dogs.",
    },
]

app = FastAPI(
    title="Movie API",
    description=description,
    version="0.0.1",
    contact={
        "name1": "Veronica Guzman",
        "email1": "vguzma08@calpoly.edu",
        "name2": "Courtney Barber",
        "email2": "cbarbe03@calpoly.edu"
    },
    openapi_tags=tags_metadata,
)
app.include_router(trainers.router)
app.include_router(classes.router)
app.include_router(dogs.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Dog Trainer API. See /docs for more information."}
