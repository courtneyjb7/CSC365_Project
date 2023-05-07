from fastapi import APIRouter, HTTPException
from src import database as db
from fastapi.params import Query
from pydantic import BaseModel
import sqlalchemy
from src.api import class_types

router = APIRouter()

# class class_sort_options(str, Enum):
#     type = "type"
#     date = "date"

@router.get("/classes/", tags=["classes"])
def get_classes(
    type: str = "", #ca
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
    # sort: class_sort_options = class_sort_options.date
):
    """
    This endpoint returns all the training classes in the database. 
    For every class, it returns:
        `class_id`: the id associated with the class
        `trainer_name`: name of the trainer
        `type`: the type of class
        `date`: the date the class take places
        `num_of_dogs_attended`: the number of dogs attending the class

        You can filter by type with the `type` query parameter.

        The `limit` and `offset` query parameters are used for pagination. 
            The `limit` query parameter specifies the maximum number 
            of results to return. 
            The `offset` query parameter specifies the
            number of results to skip before returning results.

        You can sort by date.
    """
    stmt = sqlalchemy.text("""
        SELECT classes.class_id, trainers.first_name as first, 
            trainers.last_name as last,
            class_types.type as type, date, 
            COUNT(attendance) as num_dogs
        FROM classes
        LEFT JOIN trainers on trainers.trainer_id = classes.trainer_id
        LEFT JOIN attendance on attendance.class_id = classes.class_id
        LEFT JOIN class_types on class_types.class_type_id = classes.class_type_id
        WHERE type ILIKE :type
        GROUP BY classes.class_id, first_name, last_name, class_types.type
        ORDER BY date DESC, classes.class_id  
        OFFSET :offset         
        LIMIT :limit              
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"type": f"%{type}%",
                                      "offset": offset,
                                      "limit": limit}])
        json = []
        for row in result:
            json.append(
                {
                    "class_id": row.class_id,
                    "trainer_name": row.first + " " + row.last,
                    "type": row.type,
                    "date": row.date,
                    "num_of_dogs_attended": row.num_dogs
                }
            )
    
    return json

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
                VALUES (:class_id, :trainer_id, :start, :end, :class_type)
            """)

            # INSERT INTO classes 
            # (class_id, trainer_id, date, start_time, end_time, class_type_id) 
            # VALUES (:class_id, :trainer_id, :c2, :movie_id)

            # conn.execute(stm, [{"class_id": new_class_id, "trainer_id": trainer_id}])
        return None 
    
    except Exception as error:
        print(f"Error returned: <<<{error}>>>")
        #raise HTTPException(status_code=404, detail="movie not found.")


@router.delete("/classes/{class_id}", tags=["classes"])
def delete_class(class_id: int):
    """
    This endpoint deletes a class based on its class ID.
    """
    with db.engine.begin() as conn:
        # check that class exists
        get_class(class_id)

        conn.execute(sqlalchemy.text("""DELETE 
                                     FROM classes 
                                     where class_id = :id"""), 
                                    [{"id": class_id}])

    return f"Class {class_id} deleted"

@router.put("/classes/{class_id}/{dog_id}/attendance", tags=["classes"])
def add_attendance(trainer_id: int, classes: None):
    """
    This endpoint adds a dog's attendance to a specific class.
        `attendance_id`: the id of the attendance record
        `dog_id`: the id of the dog attending
        `class_id`: the id of the class the dog is attending
        `check_in`: the timestamp the dog checked in, initialized to null
    """
    return None

@router.get("/classes/{class_id}", tags=["classes"])
def get_class(class_id: int):
    """
    This endpoint returns a specific class in the database. For every class, it returns:
        `class_id`: the id associated with the trainer
        `type`: the type of the class
        `description`: description of the class
        `trainer_first_name`: the first name of the trainer teaching the class
        `trainer_last_name`: the first name of the trainer teaching the class
        `date`: the day the class takes place
        `start_time`: the time the class starts
        `end_time`: the time the class ends
        `dogs_attended`: a dictionary of a dog's id, name, and checkin time
                            for the dogs that attended
    """
    stmt = sqlalchemy.text("""                            
        SELECT classes.class_id, trainers.first_name as first, 
            trainers.last_name as last,
            class_types.type, class_types.description, 
            date, start_time, end_time,
            dogs.dog_id, dogs.dog_name, attendance.check_in
        FROM classes
        LEFT JOIN trainers on trainers.trainer_id = classes.trainer_id
        LEFT JOIN attendance on attendance.class_id = classes.class_id
        LEFT JOIN class_types on class_types.class_type_id = classes.class_type_id
        LEFT JOIN dogs on dogs.dog_id = attendance.dog_id
        WHERE classes.class_id = :id  
        ORDER BY dogs.dog_id
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"id": class_id}])
        table = result.fetchall()
        if table == []:
            raise HTTPException(status_code=404, detail="class not found.")
        row1 = table[0]
        json = {
            "class_id": row1.class_id,
            "trainer_first_name": row1.first,
            "trainer_last_name": row1.last,
            "type": row1.type,
            "date": row1.date,
            "start_time": row1.start_time,
            "end_time": row1.end_time,
            "dogs_attended": []
        }
        if row1.dog_id is not None:
            for row in table:            
                json["dogs_attended"].append(
                    {
                        "dog_id": row.dog_id,
                        "dog_name": row.dog_name,
                        "check_in_time": row.check_in
                    }
                )
    
    return json
