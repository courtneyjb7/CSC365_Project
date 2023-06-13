from fastapi import FastAPI
from src.api import trainers, classes, dogs, class_types, rooms

description = """
Dog Training and Boarding company

<img alt="Dog Trainers Co." src="https://hips.hearstapps.com/hmg-prod/images/dog-puppy-on-garden-royalty-free-image-1586966191.jpg?crop=0.752xw:1.00xh;0.175xw,0&resize=1200:*" />
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
        "name": "class_types",
        "description": "Access information on types of classes offered.",
    },
    {
        "name": "dogs",
        "description": "Access and update information on dogs.",
    },
    {
        "name": "rooms",
        "description": "Access and update information on the rooms in the facility.",
    },
]

app = FastAPI(
    title="Dog Trainer API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Courtney Barber and Veronica Guzman",
        "email": "cbarbe03@calpoly.edu",
    },
    openapi_tags=tags_metadata,
    
)
app.include_router(trainers.router)
app.include_router(classes.router)
app.include_router(class_types.router)
app.include_router(dogs.router)
app.include_router(rooms.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Dog Trainer API. \
See /docs for more information."}
