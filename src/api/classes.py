from fastapi import APIRouter
from enum import Enum
from src import database as db
from fastapi.params import Query
from pydantic import BaseModel
import sqlalchemy
from src.api import class_types

router = APIRouter()

class class_sort_options(str, Enum):
    type = "type"
    date = "date"

@router.get("/classes/", tags=["classes"])
def get_classes(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: class_sort_options = class_sort_options.date
):
    """
    This endpoint returns all the training classes in the database. 
    For every class, it returns:
        `class_id`: the id associated with the class
        `trainer_id`: the id of the trainer teaching the class
        `type`: the type of class
        `date`: the date the class take places
        `num_of_dogs`: the number of dogs attending the class

        You can filter by type or date by using the query parameters `type` or `date`.
    """
    return None

class ClassJson(BaseModel):
    month: str
    day: str
    year: str
    start_hour: int
    start_minutes: int
    end_hour: int
    end_minutes: int
    class_type_id: int

# TODO: update documentation! - technical specification

@router.post("/classes/{trainer_id}", tags=["classes"])
def add_classes(trainer_id: int, new_class: ClassJson):
    """
    This endpoint adds a new class to a trainer's schedule.
        `date`: the day the class takes place, given by the following three values:
            • "month": string representing month of date
            • "day": string representing day of date
            • "year": string representing year of date
        `start_time`: the time the class starts, given by the following values:
            • "start_hour": int representing the hour of start_time
            • "start_minutes": int representing the minutes of start_time
        `end_time`: the time the class ends, given by the following values:
            • "end_hour": int representing the hour of end_time
            • "end_minutes": int representing the minutes of end_time
        `class_type_id`:the id of the type of class
    """

    last_class_id_txt = sqlalchemy.text("""                            
        SELECT class_id
        FROM classes
        ORDER BY class_id DESC
        LIMIT 1            
    """)

    try:

        with db.engine.begin() as conn:
            # query most recent class_id
            last_class_id = conn.execute(last_class_id_txt).fetchone()

            # calculate new class_id
            last_class_id + 1

            # get all class_types
            all_class_types = class_types.get_class_types()

            ls_class_types = [info["type_id"] for info in all_class_types]
            print(ls_class_types)
            
            # verify that new_class.class_type_id exists in the class_types; 
            # if not, throw error
            # verify trainer_id is valid
            # verify data types

            sqlalchemy.text("""
                INSERT INTO classes 
                (class_id, trainer_id, date, start_time, end_type, class_type_id)
                VALUES (:class_id, :trainer_id, :start, :end:, :class_type)
            """)

            # INSERT INTO classes 
            # (class_id, trainer_id, date, start_time, end_time, class_type_id) 
            # VALUES (:class_id, :trainer_id, :c2, :movie_id)

            # conn.execute(stm, [{"class_id": new_class_id, "trainer_id": trainer_id}])
        return None 
    
    except Exception as error:
        print(f"Error returned: <<<{error}>>>")
        #raise HTTPException(status_code=404, detail="movie not found.")

    

