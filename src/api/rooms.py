from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
import sqlalchemy
import datetime

router = APIRouter()

class RoomCriteriaJson(BaseModel):
    month: int
    day: int
    year: int
    start_hour: int
    start_minutes: int
    end_hour: int
    end_minutes: int
    class_type_id: int

def verify_date_types(class_criteria):
    class_date = datetime.date(db.try_parse(int, class_criteria.year),
                                db.try_parse(int, class_criteria.month),
                                db.try_parse(int, class_criteria.day))
    
    start_time = datetime.time(db.try_parse(int, class_criteria.start_hour),
                                db.try_parse(int, class_criteria.start_minutes))
    
    end_time = datetime.time(db.try_parse(int, class_criteria.end_hour),
                                db.try_parse(int, class_criteria.end_minutes))
    return class_date, start_time, end_time
# eventually remove endpoint and use this function in post classes?
@router.get("/rooms/", tags=["rooms"])
def get_room(month: int,
    day: int,
    year: int,
    start_hour: int,
    start_minutes: int,
    end_hour: int,
    end_minutes: int,
    class_type_id: int):
    """
    This endpoint returns a room in the facility that best meets the
    criteria of a potential class to take place there.
    Given date, start and end times, and class type, it returns
    - `room_id`: the id of the room in the facility that meets the class's needs
    - `room_name`: the name of the room
    - `max_dog_capacity`: the maximum number of dogs that can attend the class
    """
    with db.engine.connect() as conn:

        result = conn.execute(sqlalchemy.text("""
            SELECT max_num_dogs
            FROM class_types
            WHERE class_type_id = :type_id
        """), [{"type_id": criteria.class_type_id}]).one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="class type not found.")
        
        class_max = result.max_num_dogs

        date, start, end = verify_date_types(criteria)

        available_rooms = conn.execute(sqlalchemy.text("""
            SELECT room_id, max_dog_capacity
            FROM rooms
            WHERE room_id NOT IN (
                SELECT classes.room_id
                FROM classes
                JOIN rooms ON classes.room_id = rooms.room_id
                WHERE classes.date = :date AND 
                    ((CAST(:start_time AS TIME) < classes.start_time 
                        AND CAST(:end_time AS TIME) > classes.start_time)
                    OR (CAST(:start_time AS TIME) < classes.end_time 
                        AND CAST(:end_time AS TIME) > classes.end_time))
            )
            ORDER BY max_dog_capacity ASC
        """), [{
                "date": date,
                "start_time": start,
                "end_time": end
                }]).fetchall()
        
        if available_rooms != []:
            holds_class_max = list(filter(lambda x: x[1] > class_max, available_rooms))
            # avail rooms already sorted
            if len(holds_class_max):
                # select room_id with smallest capacity 
                # that fits class max if one exists
                room = holds_class_max[0][0]
                return room
            else: 
                # if no room that hold class max size, select largest room
                room = available_rooms[-1]
                raise HTTPException(status_code=404, 
                        detail=f"""the only rooms available have a max room  \
capacity > given class max. The largest room available has room_id \
{room[0]} of capacity {room[1]}""")
        else:
            raise HTTPException(status_code=404, 
                                detail="no rooms available for this date/time.")

def find_room(class_type_id, class_date, 
              start_time, end_time, conn, room):
    
    result = conn.execute(sqlalchemy.text("""
        SELECT max_num_dogs
        FROM class_types
        WHERE class_type_id = :type_id
    """), [{"type_id": class_type_id}]).one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="class type not found.")
    
    class_max = result.max_num_dogs
    
    available_rooms = conn.execute(sqlalchemy.text("""
        SELECT room_id
        FROM rooms
        WHERE room_id NOT IN (
            SELECT classes.room_id
            FROM classes
            JOIN rooms ON classes.room_id = rooms.room_id
            WHERE classes.date = :date AND 
                ((CAST(:start_time AS TIME) < classes.start_time 
                    AND CAST(:end_time AS TIME) > classes.start_time)
                OR (CAST(:start_time AS TIME) < classes.end_time 
                    AND CAST(:end_time AS TIME) > classes.end_time)
                OR (CAST(:start_time AS TIME) = classes.start_time 
                    AND CAST(:end_time AS TIME) = classes.end_time))
        )
        ORDER BY max_dog_capacity ASC
    """), [{
            "date": class_date,
            "start_time": start_time,
            "end_time": end_time
            }]).fetchall()
    
    if room not in available_rooms:
        raise HTTPException(status_code=404, 
                            detail="the provided room is unavailable at this day/time.")