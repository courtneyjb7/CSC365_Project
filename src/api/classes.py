from fastapi import APIRouter, HTTPException
from src import database as db
from fastapi.params import Query
from pydantic import BaseModel
import sqlalchemy
import datetime
from enum import Enum
from src.api import rooms


router = APIRouter()

# TODO: filter by type, if given a type as an integer
@router.get("/classes/", tags=["classes"])
def get_classes(
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
):
    """
    This endpoint returns all the training classes in the database. 
    For every class, it returns:
    - `class_id`: the id associated with the class
    - `trainer_id: the id of the trainer
    - `trainer_name`: name of the trainer
    - `type`: the type of class
    - `date`: the date the class takes place on
    - `num_of_dogs_attended`: the number of dogs attending the class
    - `room_id`: the id of the room the class takes place in

    You can filter by type with the `type` query parameter.
    You can `limit` and `offset` the results. 

    Classes are sorted by date in descending order.
    """
    stmt = sqlalchemy.text("""
        SELECT classes.class_id, trainers.first_name as first, 
            trainers.last_name as last,
            class_types.type as type, date, 
            COUNT(attendance) as num_dogs,
            trainers.trainer_id as trainer_id,
            classes.room_id
        FROM classes
        LEFT JOIN trainers on trainers.trainer_id = classes.trainer_id
        LEFT JOIN attendance on attendance.class_id = classes.class_id
        LEFT JOIN class_types on class_types.class_type_id = classes.class_type_id
        GROUP BY classes.class_id, first_name, last_name, 
                class_types.type, trainers.trainer_id
        ORDER BY date DESC, classes.class_id  
        OFFSET :offset         
        LIMIT :limit              
    """)
    
    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"offset": offset,
                                      "limit": limit}])
        json = []
        for row in result:
            json.append(
                {
                    "class_id": row.class_id,
                    "trainer_id": row.trainer_id,
                    "trainer_name": row.first + " " + row.last,
                    "type": row.type,
                    "date": row.date,
                    "num_of_dogs_attended": row.num_dogs,
                    "room_id": row.room_id
                }
            )
    
    return json

class ClassJson(BaseModel):
    trainer_id: int
    month: int
    day: int
    year: int
    start_hour: int
    start_minutes: int
    end_hour: int
    end_minutes: int
    class_type_id: int
    room_id: int

@router.post("/classes/", tags=["classes"])
def add_classes(new_class: ClassJson):
    """
    This endpoint adds a new class to a trainer's schedule.
    - `trainer_id`: id of the trainer teaching the class
    - `date`: the day the class takes place, given by the following three values:
        - "month": int representing month number of date
        - "day": int representing day number of date
        - "year": int representing year number of date
    - `start_time`: the time the class starts, given by the following values:
        - "start_hour": int representing the hour of start_time
        - "start_minutes": int representing the minutes of start_time
    - `end_time`: the time the class ends, given by the following values:
        - "end_hour": int representing the hour of end_time
        - "end_minutes": int representing the minutes of end_time
    - `class_type_id`:the id of the type of class
    - `room_id`: the id of the room the trainer wants to teach the class in
    """

    try:

        with db.engine.begin() as conn:

            stm = sqlalchemy.text("""
                INSERT INTO classes 
                (trainer_id, date, start_time, end_time, class_type_id, room_id)
                VALUES (:trainer_id, :date, :start, :end, :class_type, :room)
            """)

            # verify data types
            class_date = datetime.date(db.try_parse(int, new_class.year),
                                       db.try_parse(int, new_class.month),
                                       db.try_parse(int, new_class.day))
            
            start_time = datetime.time(db.try_parse(int, new_class.start_hour),
                                       db.try_parse(int, new_class.start_minutes))
            
            end_time = datetime.time(db.try_parse(int, new_class.end_hour),
                                       db.try_parse(int, new_class.end_minutes))

            # check that room is available at given date/time
            rooms.find_room(class_date, start_time, end_time, conn, new_class.room_id)

            conn.execute(stm, [
                { 
                    "trainer_id": new_class.trainer_id,
                    "date": class_date,
                    "start": start_time,
                    "end": end_time,
                    "class_type": new_class.class_type_id,
                    "room": new_class.room_id
                }
            ])

            return "success"
    
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise


@router.delete("/classes/{class_id}", tags=["classes"])
def delete_class(class_id: int):
    """
    This endpoint deletes a class based on its class ID.
    """
    try:
        with db.engine.begin() as conn:
            result = conn.execute(sqlalchemy.text("""SELECT class_id
                                            FROM classes 
                                            where class_id = :id
                                        """), 
                                        [{"id": class_id}]).one_or_none()
            if result is None:
                raise HTTPException(status_code=404, 
                                    detail=("class_id does not exist in classes table."))

            conn.execute(sqlalchemy.text("""DELETE 
                                        FROM classes 
                                        where class_id = :id"""), 
                                        [{"id": class_id}])

        return "success"
    
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise



@router.post("/classes/{class_id}/attendance", tags=["classes"])
def add_attendance(class_id: int, dog_id: int):
    """
    This endpoint adds a dog's attendance to a specific class.
    - `attendance_id`: the id of the attendance record
    - `dog_id`: the id of the dog attending
    - `class_id`: the id of the class the dog is attending
    - `check_in`: the timestamp the dog checked in
        - "month": int representing month number of date
        - "day": int representing day number of date
        - "year": int representing year number of date
        - "hour": int representing the hour dog was checked in
        - "minutes": int representing the minutes dog was checked in
    """

    try:

        with db.engine.begin() as conn:
            # TODO: attendance entity and enrolled entity
            stm = sqlalchemy.text("""
                SELECT attendance_id
                FROM attendance
                WHERE dog_id = :dog_id AND class_id = :class_id               
            """)
            result = conn.execute(stm, [
                {
                    "dog_id": dog_id,
                    "class_id": class_id,
                }
            ]).one_or_none()
            if result is not None:
                raise HTTPException(status_code=404, 
                                    detail="dog already checked into this class.")
            stm = sqlalchemy.text("""
                INSERT INTO attendance 
                (dog_id, class_id)
                VALUES (:dog_id, :class_id)                
            """)

            conn.execute(stm, [
                {
                    "dog_id": dog_id,
                    "class_id": class_id,
                }
            ])

            return "success"

    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise
        


@router.get("/classes/{class_id}", tags=["classes"])
def get_class(class_id: int):
    """
    This endpoint returns a specific class in the database. For every class, it returns:
    - `class_id`: the id associated with the trainer
    - `type`: the type of the class
    - `description`: description of the class
    - `trainer_id`: the id of the trainer teaching the class
    - `trainer_first_name`: the first name of the trainer 
    - `trainer_last_name`: the first name of the trainer 
    - `date`: the day the class takes place
    - `start_time`: the time the class starts
    - `end_time`: the time the class ends
    - `room_id`: the id of the room the class takes place in
    - `room_name`: the name of the room the class takes place in
    - `dogs_attended`: a dictionary of a dog's id, name, and checkin time
                        for the dogs that attended
    """
    stmt = sqlalchemy.text("""                            
        SELECT classes.class_id, trainers.first_name as first, 
            trainers.last_name as last,
            class_types.type, class_types.description, 
            date, start_time, end_time,
            dogs.dog_id, dogs.dog_name, attendance.check_in,
            trainers.trainer_id as trainer_id, 
            rooms.room_id, room_name
        FROM classes
        LEFT JOIN trainers on trainers.trainer_id = classes.trainer_id
        LEFT JOIN attendance on attendance.class_id = classes.class_id
        LEFT JOIN class_types on class_types.class_type_id = classes.class_type_id
        LEFT JOIN dogs on dogs.dog_id = attendance.dog_id
        LEFT JOIN rooms ON rooms.room_id = classes.room_id
        WHERE classes.class_id = :id  
        ORDER BY dogs.dog_id
    """)
    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"id": class_id}])

        dogs_attending =  result.fetchall()
        
        if dogs_attending == []:
            raise HTTPException(status_code=404, detail="class not found.")
        
        class_info = dogs_attending[0]  
        json = {
            "class_id": class_info.class_id,
            "trainer_id": class_info.trainer_id,
            "trainer_first_name": class_info.first,
            "trainer_last_name": class_info.last,
            "type": class_info.type,
            "date": class_info.date,
            "start_time": class_info.start_time,
            "end_time": class_info.end_time,
            "room_id": class_info.room_id,
            "room_name": class_info.room_name,
            "dogs_attended": []
        }

        if class_info.dog_id is not None:
            for row in dogs_attending:            
                json["dogs_attended"].append(
                    {
                        "dog_id": row.dog_id,
                        "dog_name": row.dog_name,
                        "check_in_time": row.check_in
                    }
                )
    
    return json

class DayOptions(str, Enum):
    sun = "Sunday"
    mon = "Monday"
    tues = "Tuesday"
    wed = "Wednesday"
    thurs = "Thursday"
    fri = "Friday"
    sat = "Saturday"    

class time_options(str, Enum):
    morning = "morning"
    midday = "midday"
    afternoon = "afternoon"

@router.get("/classes/available/", tags=["classes"])
def find_classes(class_type_id: int = 1,
                 time_range: time_options = time_options.midday,                 
                 day1: DayOptions = DayOptions.sun,
                 day2: DayOptions = None,
                 day3: DayOptions = None,
                 day4: DayOptions = None,
                 day5: DayOptions = None,
                 day6: DayOptions = None,
                 day7: DayOptions = None,
                 limit: int = Query(50, ge=1, le=250)
):                 
    """
    This endpoint finds classes that meet the given criteria.
    It accepts a time range and any days of the week dog is available, 
    and the class type the dog needs.
    For every class, it returns:
    - `class_id`: the id associated with the class
    - `trainer_id: the id of the trainer
    - `type`: the type of class
    - `date`: the date the class takes place on
    - `start_time`: the time the class starts
    - `end_time`: the time the class ends
    """
    if time_range == "morning":
        time_range = ("08:00:00", "11:00:00")
    elif time_range == "midday":
        time_range = ("11:00:00", "14:00:00")
    else:
        time_range = ("14:00:00", "17:00:00")

    with db.engine.connect() as conn:
        
        valid_classes = conn.execute(sqlalchemy.text("""
            SELECT class_id, trainer_id, type, date,
                start_time, end_time
            FROM classes
            JOIN class_types ON 
                class_types.class_type_id = classes.class_type_id
            WHERE classes.class_type_id = :type_id AND 
                date > CURRENT_DATE AND
                (to_char(date, 'Day') LIKE :day1 OR
                to_char(date, 'Day') LIKE :day2 OR
                to_char(date, 'Day') LIKE :day3 OR
                to_char(date, 'Day') LIKE :day4 OR
                to_char(date, 'Day') LIKE :day5 OR
                to_char(date, 'Day') LIKE :day6 OR
                to_char(date, 'Day') LIKE :day7) AND
                (CAST(:range_start AS TIME) < start_time AND 
                    CAST(:range_end AS TIME) > end_time)
            ORDER BY date ASC
            LIMIT :limit
        """), [{
                "type_id": class_type_id,
                "day1": f"%{day1}%",
                "day2": f"%{day2}%",
                "day3": f"%{day3}%",
                "day4": f"%{day4}%",
                "day5": f"%{day5}%",
                "day6": f"%{day6}%",
                "day7": f"%{day7}%",
                "limit": limit,
                "range_start": time_range[0],
                "range_end": time_range[1]
                }]).fetchall()
        json = []
        for row in valid_classes:
            json.append(
                {
                    "class_id": row.class_id,
                    "trainer_id": row.trainer_id,
                    "type": row.type,
                    "date": row.date,
                    "start_time": row.start_time,
                    "end_time": row.end_time
                }
            )
        if json == []:
            return "There are no classes that match this criteria."
        return json
    
        
        