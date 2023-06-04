from fastapi import APIRouter, HTTPException
from src import database as db
from fastapi.params import Query
from pydantic import BaseModel
import sqlalchemy
import datetime
from enum import Enum
from src.api import rooms


router = APIRouter()


@router.get("/classes/{id}", tags=["classes"])
def get_class(id: int):
    """
    This endpoint returns a specific class in the database. For every class, it returns:
    - `class_id`: the id associated with the class
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
        result = conn.execute(stmt, [{"id": id}])

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
    morning = "morning (8AM-11AM)"
    midday = "midday (11AM-2PM)"
    afternoon = "afternoon (2PM-5PM)"


@router.get("/classes/", tags=["classes"])
def get_classes(class_type_id: int = None,
                 date: str = None,
                 trainer_id: int = None,
                 time_range: time_options = None,                 
                 day1: DayOptions = None,
                 day2: DayOptions = None,
                 day3: DayOptions = None,
                 day4: DayOptions = None,
                 day5: DayOptions = None,
                 day6: DayOptions = None,
                 day7: DayOptions = None,
                 limit: int = Query(50, ge=1, le=250)
                 
):    
    # has complex transaction             
    """
    This endpoint finds classes that meet the given criteria. 
    You can filter by trainer_id, class_type_id, a time range, and
    days of the week. If a date is specified, only classes that 
    occur on or after the date will be returned. 
    It accepts a limit and is sorted by date in ascending order. 

    For every class, it returns:
    - `class_id`: the id associated with the class
    - `trainer_id`: the id of the trainer
    - `trainer_name`: first and last name of the trainer
    - `type`: the type of class
    - `date`: the date the class takes place on
    - `start_time`: the time the class starts
    - `end_time`: the time the class ends
    - `room_id`: the id of the room the class takes place in
    - `num_of_dogs_attended`: the number of dogs attending the class
    """
    if time_range == time_options.morning:
        time_range = ("08:00:00 AM", "11:00:00 AM")
    elif time_range == time_options.midday:
        time_range = ("11:00:00 AM", "2:00:00 PM")
    elif time_range == time_options.afternoon:
        time_range = ("2:00:00 PM", "5:00:00 PM")
    else:
        time_range = (None, None)
    

    with db.engine.connect() as conn:
        
        valid_classes = conn.execute(sqlalchemy.text("""
            SELECT classes.class_id, classes.trainer_id, type, classes.date,
                start_time, end_time, trainers.first_name,
                trainers.last_name, room_id,
                COUNT(attendance) as num_dogs
            FROM classes
            
            JOIN trainers ON trainers.trainer_id = classes.trainer_id
            JOIN class_types ON 
                class_types.class_type_id = classes.class_type_id
            LEFT JOIN attendance on attendance.class_id = classes.class_id

            WHERE (:date IS NULL OR classes.date >= CAST(:date AS DATE)) AND 
                (classes.class_type_id = :type_id OR :type_id IS NULL) AND
                (to_char(date, 'Day') ILIKE :day1 OR
                to_char(date, 'Day') ILIKE :day2 OR
                to_char(date, 'Day') ILIKE :day3 OR
                to_char(date, 'Day') ILIKE :day4 OR
                to_char(date, 'Day') ILIKE :day5 OR
                to_char(date, 'Day') ILIKE :day6 OR
                to_char(date, 'Day') ILIKE :day7 OR
                :day1 = '%None%'
                ) AND
                (:range_start IS NULL OR
                    (CAST(:range_start AS TIME) <= classes.start_time 
                    AND CAST(:range_end AS TIME) >= classes.start_time)
                    AND (CAST(:range_start AS TIME) <= classes.end_time 
                    AND CAST(:range_end AS TIME) >= classes.end_time))
                AND (:trainer_id IS NULL OR classes.trainer_id = :trainer_id)

            GROUP BY classes.class_id, classes.trainer_id, type, classes.date,
                start_time, end_time, trainers.first_name,
                trainers.last_name, room_id

            ORDER BY date ASC
            LIMIT :limit
        """), [{
                "type_id": class_type_id,
                "date": date,
                "day1": f"%{day1}%",
                "day2": f"%{day2}%",
                "day3": f"%{day3}%",
                "day4": f"%{day4}%",
                "day5": f"%{day5}%",
                "day6": f"%{day6}%",
                "day7": f"%{day7}%",
                "limit": limit,
                "range_start": time_range[0],
                "range_end": time_range[1],
                "trainer_id": trainer_id
                }]).fetchall()
        json = []
        for row in valid_classes:
            json.append(
                {
                    "class_id": row.class_id,
                    "trainer_id": row.trainer_id,
                    "trainer_name": row.first_name + " " + row.last_name,
                    "type": row.type,
                    "date": row.date,
                    "start_time": row.start_time,
                    "end_time": row.end_time,
                    "room_id": row.room_id,
                    "num_dogs_attended": row.num_dogs
                }
            )
        if json == []:
            return "There are no classes that match this criteria."
        return json
    


class ClassJson(BaseModel):
    trainer_id: int
    date: str = "yyyy-mm-dd"
    start_time: str = "hh:mm AM/PM"
    end_time: str = "hh:mm AM/PM"
    class_type_id: int
    room_id: int
    

@router.post("/classes/", tags=["classes"])
def add_classes(new_class: ClassJson):
    
    """
    This endpoint adds a new class to a trainer's schedule.
    - `trainer_id`: id of the trainer teaching the class
    - `date`: the day the class takes place, given by:
        - "yyyy-mm-dd": provide a string with the year, month, and day seperated by hyphen (-)
    - `start_time`: the time the class starts, given by:
        - "hh:mm AM/PM": provide a string with the hour and minutes seperated with a colon, as well as an indication whether time is AM or PM
    - `end_time`: the time the class ends, given by the following values:
        - "hh:mm AM/PM": provide a string with the hour and minutes seperated with a colon, as well as an indication whether time is AM or PM
    - `class_type_id`:the id of the type of class
    - `room_id`: the id of the room the trainer wants to teach the class in
    """

    try:

        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
            with conn.begin():

                stm = sqlalchemy.text("""
                    INSERT INTO classes 
                    (trainer_id, date, start_time, end_time, class_type_id, room_id)
                    VALUES (:trainer_id, :date, :start, :end, :class_type, :room)
                    RETURNING class_id
                """)

                # convert from string format to datetime format
                class_date = datetime.datetime.strptime(new_class.date, "%Y-%m-%d").date()
                start_time = datetime.datetime.strptime(new_class.start_time, "%I:%M %p").time()
                end_time = datetime.datetime.strptime(new_class.end_time, "%I:%M %p").time()
                
                if end_time < start_time:                                
                    raise HTTPException(status_code=404, detail="end_time should be after start_time")
                    
                # check that room is available at given date/time
                rooms.find_room(class_date, start_time, end_time, conn, new_class.room_id)

                class_id = conn.execute(stm, [
                    { 
                        "trainer_id": new_class.trainer_id,
                        "date": class_date,
                        "start": start_time,
                        "end": end_time,
                        "class_type": new_class.class_type_id,
                        "room": new_class.room_id
                    }
                ]).scalar_one()

                return f"class_id added: {class_id}"
    
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise


@router.post("/classes/{id}/attendance", tags=["classes"])
def add_attendance(id: int, dog_id: int):
    """
    This endpoint adds a dog's attendance to a specific class.
    - `attendance_id`: the id of the attendance record
    - `dog_id`: the id of the dog attending
    - `id`: the id of the class the dog is attending
    """

    try:

        with db.engine.begin() as conn:
            stm = sqlalchemy.text("""
                SELECT attendance_id
                FROM attendance
                WHERE dog_id = :dog_id AND class_id = :class_id               
            """)
            result = conn.execute(stm, [
                {
                    "dog_id": dog_id,
                    "class_id": id,
                }
            ]).one_or_none()
            if result is not None:
                raise HTTPException(status_code=404, 
                                    detail="dog already checked into this class.")
            stm = sqlalchemy.text("""
                INSERT INTO attendance 
                (dog_id, class_id)
                VALUES (:dog_id, :class_id) RETURNING attendance_id               
            """)

            attendance_id = conn.execute(stm, [
                {
                    "dog_id": dog_id,
                    "class_id": id,
                }
            ])

            return f"attendance_id added: {attendance_id}" 

    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise
        

@router.delete("/classes/{id}", tags=["classes"])
def delete_class(id: int):
    """
    This endpoint deletes a class based on its class ID.
    """
    try:
        with db.engine.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
            with conn.begin():
                result = conn.execute(sqlalchemy.text("""SELECT class_id
                                                FROM classes 
                                                where class_id = :id
                                            """), 
                                            [{"id": id}]).one_or_none()
                if result is None:
                    raise HTTPException(status_code=404, 
                            detail=("class_id does not exist in classes table."))

                conn.execute(sqlalchemy.text("""DELETE 
                                            FROM classes 
                                            where class_id = :id"""), 
                                            [{"id": id}])

                return f"class_id deleted: {id}"
    
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise
