from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
import datetime

router = APIRouter()


def verify_date_types(month, day, year, 
        start_hour, start_minutes, end_hour, end_minutes):
    class_date = datetime.date(year, month, day)
    
    start_time = datetime.time(start_hour, start_minutes)
    
    end_time = datetime.time(end_hour, end_minutes)

    return class_date, start_time, end_time


@router.get("/rooms/", tags=["rooms"])
def get_room(
        month: int,
        day: int,
        year: int,
        start_hour: int,
        start_minutes: int,
        end_hour: int,
        end_minutes: int,
        class_type_id: int
    ):
    """
    This endpoint returns a room_id of a room in the facility that best meets the
    criteria of a potential class to take place there. 
    It returns the smallest room that is available at the given time and
    has a max dog capacity greater than the given class type's
    max number of dogs. If the only available rooms are smaller than the class type max,
    it throws an error but says what the largest room available is.

    The endpoint accepts:
    - `month`: month you want to schedule class
    - `day`: day you want to schedule class
    - `year`: year you want to schedule class
    - `start_hour`: start_time hour
    - `start_minutes`: start_time minutes
    - `end_hour`: end_time hour
    - `end_minute`: end_time minutes
    - `class type`: id of a type of class you are interested in signing a dog up for

    It returns:
    - `room_id`: the id of the room in the facility that meets the class's needs
    - `room_name`: the name of the room
    - `max_dog_capacity`: the maximum number of dogs that can attend the class
    """
    try:
        with db.engine.connect() as conn:

            result = conn.execute(sqlalchemy.text("""
                SELECT max_num_dogs
                FROM class_types
                WHERE class_type_id = :type_id
            """), [{"type_id": class_type_id}]).one_or_none()
            if result is None:
                raise HTTPException(status_code=404, detail="class type not found.")
            
            class_max = result.max_num_dogs

            date, start, end = verify_date_types(month, 
                                                day, 
                                                year, 
                                                start_hour, 
                                                start_minutes, 
                                                end_hour, 
                                                end_minutes)

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
                holds_class_max = list(filter(lambda x: x[1] >= class_max, 
                                              available_rooms))
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
                            detail=f"""the only rooms available have a max room \
capacity < given class max size. The largest room available has room_id \
{room[0]} of capacity {room[1]}""")
            else:
                raise HTTPException(status_code=404, 
                                    detail="no rooms available for this date/time.")
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise



def find_room(class_date, start_time, end_time, conn, room_id):
    # This function is used by add_classes to 
    # check that the given room is available 

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
    
    room_avail = list(filter(lambda x: x[0] == room_id, available_rooms))

    if room_avail == []:
        raise HTTPException(status_code=404, 
                            detail="the provided room is unavailable at this day/time.")