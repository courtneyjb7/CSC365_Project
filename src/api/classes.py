from fastapi import APIRouter, HTTPException
from src import database as db
from fastapi.params import Query
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.exc import IntegrityError
import datetime

router = APIRouter()


@router.get("/classes/", tags=["classes"])
def get_classes(
    type: str = "", 
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
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

        Classes are sorted by date in descending order.
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
    month: int
    day: int
    year: int
    start_hour: int
    start_minutes: int
    end_hour: int
    end_minutes: int
    class_type_id: int

@router.post("/classes/{trainer_id}", tags=["classes"])
def add_classes(trainer_id: int, new_class: ClassJson):
    """
    This endpoint adds a new class to a trainer's schedule.
        `date`: the day the class takes place, given by the following three values:
            • "month": int representing month number of date
            • "day": int representing day number of date
            • "year": int representing year number of date
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

            new_class_id = last_class_id[0] + 1

            stm = sqlalchemy.text("""
                INSERT INTO classes 
                (class_id, trainer_id, date, start_time, end_time, class_type_id)
                VALUES (:class_id, :trainer_id, :date, :start, :end, :class_type)
            """)

            # verify data types
            class_date = datetime.date(db.try_parse(int, new_class.year),
                                       db.try_parse(int, new_class.month),
                                       db.try_parse(int, new_class.day))
            
            start_time = datetime.time(db.try_parse(int, new_class.start_hour),
                                       db.try_parse(int, new_class.start_minutes))
            
            end_time = datetime.time(db.try_parse(int, new_class.end_hour),
                                       db.try_parse(int, new_class.end_minutes))

            conn.execute(stm, [
                {
                    "class_id": new_class_id, 
                    "trainer_id": trainer_id,
                    "date": class_date,
                    "start": start_time,
                    "end": end_time,
                    "class_type": new_class.class_type_id,
                }
            ])

            return new_class_id
        
    except IntegrityError:
        print("Error returned: <<<foreign key violation>>>")
    
    except Exception as error:
        print(f"Error returned: <<<{error}>>>")


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


class AttendanceJson(BaseModel):
    month: int
    day: int
    year: int
    hour: int
    minutes: int


@router.put("/classes/{class_id}/{dog_id}/attendance", tags=["classes"])
def add_attendance(class_id: int, dog_id: int, attd: AttendanceJson):
    """
    This endpoint adds a dog's attendance to a specific class.
        `attendance_id`: the id of the attendance record
        `dog_id`: the id of the dog attending
        `class_id`: the id of the class the dog is attending
        `check_in`: the timestamp the dog checked in
            • "month": int representing month number of date
            • "day": int representing day number of date
            • "year": int representing year number of date
            • "hour": int representing the hour dog was checked in
            • "minutes": int representing the minutes dog was checked in
    """

    # TODO: should check_in be able to be null? like give a null value for month, 
    # and all other fields

    try:

        with db.engine.begin() as conn:
            # TODO: attendance entity and enrolled entity

            check_in = datetime.datetime(
                    db.try_parse(int, attd.year),
                    db.try_parse(int, attd.month),
                    db.try_parse(int, attd.day),
                    db.try_parse(int, attd.hour),
                    db.try_parse(int, attd.minutes)
                )

            # does an attendance already exist for the dog_id in that class_id?
            stm = sqlalchemy.text("""                            
                SELECT *
                FROM attendance
                WHERE dog_id = :dog_id and class_id = :class_id           
            """)

            attendance = conn.execute(stm, [{
                "dog_id": dog_id,
                "class_id": class_id
            }]).fetchone()


            if attendance is not None:  # if yes, then update
                stm = sqlalchemy.text("""                            
                    UPDATE attendance
                    SET check_in = :check_in
                    WHERE dog_id = :dog_id 
                    and class_id = :class_id 
                    and attendance_id = :attendance_id     
                """)

                conn.execute(stm, [
                    {
                        "attendance_id": attendance[0], 
                        "dog_id": dog_id,
                        "class_id": class_id,
                        "check_in": check_in,
                    }
                ])

            else:   # if no, then insert, get last attendance id

                last_attendance_id_txt = sqlalchemy.text("""                            
                    SELECT attendance_id
                    FROM attendance
                    ORDER BY attendance_id DESC
                    LIMIT 1            
                """)

                last_attendance_id = conn.execute(last_attendance_id_txt).fetchone()[0]

                new_id = last_attendance_id + 1

                stm = sqlalchemy.text("""
                    INSERT INTO attendance 
                    (attendance_id, dog_id, class_id, check_in)
                    VALUES (:attendance_id, :dog_id, :class_id, :check_in)
                """)

                conn.execute(stm, [
                    {
                        "attendance_id": new_id, 
                        "dog_id": dog_id,
                        "class_id": class_id,
                        "check_in": check_in,
                    }
                ])

        return new_id
    
    except IntegrityError:
        print("Error returned: <<<foreign key violation>>>")

    except Exception as error:
        print(f"Error returned: <<<{error}>>>")


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
