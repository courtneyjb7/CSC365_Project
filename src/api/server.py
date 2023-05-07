from fastapi import FastAPI
from src.api import trainers, classes, class_types

description = """
Dog Training and Boarding company
"""
tags_metadata = [
    {
        "name": "classes",
        "description": "Access information on classes available.",
    },
    {
        "name": "trainers",
        "description": "Access information on trainers.",
    },
    {
        "name": "class_types",
        "description": "Access information on types of classes offered.",
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
app.include_router(class_types.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Dog Trainer API. \
            See /docs for more information."}
