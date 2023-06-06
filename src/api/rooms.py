from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
import datetime

router = APIRouter()


@router.get("/rooms/", tags=["rooms"])
def get_room(
        class_type_id: int,
        date: str = "yyyy-mm-dd",
        start_time: str = "hh:mm AM",
        end_time: str = "hh:mm AM"        
    ):
    
    """
    This endpoint returns a room_id of a room in the facility that best meets the
    criteria of a potential class to take place there. 
    It returns the smallest room that is available at the given time and
    has a max dog capacity greater than the given class type's
    max number of dogs. If the only available rooms are smaller than the class type max,
    it throws an error but says what the largest room available is.

    Given:
    - `class type`: class you are interested in signing up a dog for
    - `date`: the day the class takes place, given by:
        - "yyyy-mm-dd": provide a string with the year, month, and day 
            seperated by hyphen (-)
    - `start_time`: the time the class starts, given by:
        - "hh:mm AM/PM": provide a string with the hour and minutes 
            seperated with a colon, 
        as well as an indication whether time is AM or PM
    - `end_time`: the time the class ends, given by:
        - "hh:mm AM/PM": provide a string with the hour 
        and minutes seperated with a colon, 
        as well as an indication whether time is AM or PM
    it returns:
    - `room_id`: the id of the room in the facility that meets the class's needs
    - `room_name`: the name of the room
    - `max_dog_capacity`: the maximum number of dogs that can fit in the room
    - `max_class_size`: the max number of dogs that can 
        attend a class of the given class type
    """
    try:
        with db.engine.connect() \
        .execution_options(isolation_level="SERIALIZABLE") as conn:
            with conn.begin():
            
                date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                start_time = datetime.datetime.strptime(start_time, "%I:%M %p").time()
                end_time = datetime.datetime.strptime(end_time, "%I:%M %p").time()
                
                if end_time < start_time:                                
                    raise HTTPException(status_code=404, 
                                        detail="end_time should be after start_time")
                 
                result = conn.execute(sqlalchemy.text("""
                    SELECT max_num_dogs
                    FROM class_types
                    WHERE class_type_id = :type_id
                """), [{"type_id": class_type_id}]).one_or_none()
                if result is None:
                    raise HTTPException(status_code=404, detail="class type not found.")
                
                class_max = result.max_num_dogs

                available_rooms = conn.execute(sqlalchemy.text("""
                    SELECT room_id, max_dog_capacity, room_name
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
                        "start_time": start_time,
                        "end_time": end_time
                        }]).fetchall()
                
                if available_rooms != []:
                    #get available rooms with max dog capacity > class max 
                    holds_class_max = list(filter(lambda x: x[1] >= class_max, 
                                                available_rooms))
                    # avail rooms already sorted

                    if len(holds_class_max):
                        # select room_id with smallest capacity 
                        # that fits class max if one exists
                        room = {
                            "room_id": holds_class_max[0][0],
                            "room_name": holds_class_max[0][2],
                            "max_dog_capacity": holds_class_max[0][1],
                            "max_class_size": class_max
                        }
                        return room
                    else: 
                        # if no room that holds class max size, select largest room
                        room = {
                            "room_id": available_rooms[-1][0],
                            "room_name": available_rooms[-1][2],
                            "max_dog_capacity": available_rooms[-1][1],
                            "max_class_size": class_max
                        }

                        raise HTTPException(status_code=404, 
                                detail=f"""the only rooms available have a max room \
capacity < given class max size. The largest room available is {room}""")
                    
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
    # has complex transaction
    available_rooms = conn.execute(sqlalchemy.text("""
        SELECT room_id
        FROM rooms
        WHERE room_id NOT IN (
            SELECT classes.room_id
            FROM classes
            JOIN rooms ON classes.room_id = rooms.room_id
            WHERE classes.date = :date AND 
                ((CAST(:start_time AS TIME) <= classes.start_time 
                    AND CAST(:end_time AS TIME) > classes.start_time)
                OR (CAST(:start_time AS TIME) < classes.end_time 
                    AND CAST(:end_time AS TIME) >= classes.end_time)
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