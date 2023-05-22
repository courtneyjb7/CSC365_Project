from fastapi import APIRouter, HTTPException
from src import database as db
from fastapi.params import Query
from pydantic import BaseModel
import sqlalchemy
import datetime

router = APIRouter()

# TODO: filter by type, if given a type as an integer
@router.get("/classes/", tags=["classes"])
def get_room()