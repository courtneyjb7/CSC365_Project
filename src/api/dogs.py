from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
from pydantic import BaseModel
from fastapi.params import Query

router = APIRouter()


@router.get("/dogs/{id}", tags=["dogs"])
def get_dog(id: int):
    """
    This endpoint returns information about a dog in the database. 
    For every dog, it returns:
    - `id`: the id associated with the dog
    - `name`: the name of the dog
    - `client_email`: the email of the owner of the dog
    - `birthday`: the dog's date of birth
    - `breed`: the dog's breed
    - `trainer_comments`: a list of comments from the 
            trainer about the dog's progress 

    Each comment returns:
    - `comment_id`: the id of the comment
    - `trainer`: the name of the trainer who wrote the comment
    - `time_added`: the day and time the comment was made
    - `text`: the comment text

    """
    stmt = sqlalchemy.text("""                            
        SELECT dogs.dog_id, dogs.dog_name, dogs.client_email, 
            dogs.birthday, dogs.breed, comments.comment_id,
            comments.time_added, comments.comment_text,
            trainers.first_name, trainers.last_name
        FROM dogs
        LEFT JOIN comments on comments.dog_id = dogs.dog_id
        LEFT JOIN trainers on comments.trainer_id = trainers.trainer_id
        WHERE dogs.dog_id = :id
        ORDER BY comments.time_added desc
    """)
    attendance_stmt = sqlalchemy.text("""                            
        SELECT class_id, check_in
        FROM attendance
        WHERE dog_id = :id
        ORDER BY class_id
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"id": id}])
        dog_comments_info = result.fetchall()
        if dog_comments_info == []:
            raise HTTPException(status_code=404, detail="dog not found.")
        dog_info = dog_comments_info[0]
        json = {
            "dog_id": dog_info.dog_id,
            "name": dog_info.dog_name,
            "client_email": dog_info.client_email, 
            "birthday": dog_info.birthday,
            "breed": dog_info.breed,
            "trainer_comments": [],
            "classes_attended": []
        }
        if dog_info.comment_id is not None:
            for row in dog_comments_info:
                json["trainer_comments"].append(
                    {
                        "comment_id": row.comment_id,
                        "trainer": row.first_name + " " + row.last_name,
                        "time_added": row.time_added,
                        "text": row.comment_text
                    }
                )
        dog_attendance = conn.execute(attendance_stmt, [{"id": id}]).fetchall()
        for row in dog_attendance:
            json["classes_attended"].append(
                {
                    "class_id": row.class_id,
                    "check_in": row.check_in
                }
            )
    
    return json


class CommentJson(BaseModel):
    trainer_id: int
    class_id: int
    comment_text: str


@router.post("/dogs/{id}/comments", tags=["dogs"])
def add_comments(id: int, new_comment: CommentJson):
    """
    This endpoint updates trainer comments for a dog. 
    - `id`: the id of the dog the comment is about

    Provide a body json with the following information:
    - `trainer_id`: the id of the trainer who made the comment
    - `comment_text`: a string from the trainer about the dog's progress   
    """

    try:

        with db.engine.begin() as conn:

            stmt = sqlalchemy.text("""
                INSERT INTO comments
                ( dog_id, trainer_id, comment_text)
                VALUES (:dog_id, :trainer_id, :text)
                RETURNING comment_id
            """)

            comment_id = conn.execute(stmt, [{
                "dog_id": id,
                "trainer_id": db.try_parse(int, new_comment.trainer_id), 
                "text": new_comment.comment_text
            }]).scalar_one()

        return f"comment_id added: {comment_id}"  
    
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise

@router.get("/dogs/", tags=["dogs"])
def get_dogs(
    name: str = "", 
    breed: str = "",
    client_email: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
):
    """
    This endpoint returns all the dogs in the database. 
    For every dog, it returns:
    - `dog_id`: the id associated with the dog
    - `dog_name`: the name of the dog
    - `birthday`: the birthday of the dog
    - `breed`: the dog's breed
    - `client_email`: the email of the owner of the dog
     """

    stmt = sqlalchemy.text("""                            
        SELECT dog_id, dog_name, birthday, breed, client_email
        FROM dogs 
        WHERE dog_name ILIKE :name 
        AND breed ILIKE :breed
        AND client_email ILIKE :client_email
        OFFSET :offset         
        LIMIT :limit            
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"name": f"{name}%",
                                      "breed": f"{breed}%",
                                      "client_email": f"{client_email}%",
                                      "offset": offset,
                                      "limit": limit}])
        json = []
        for row in result:
            json.append(
                {
                    "dog_id": row.dog_id,
                    "name": row.dog_name,
                    "birthday": row.birthday,
                    "breed": row.breed,
                    "client_email": row.client_email
                }
            )

    return json


@router.delete("/dogs/comments/{id}", tags=["dogs"])
def delete_comments(id: int):
    """
    This endpoint deletes a comment for a dog based on its comment ID.
    """
    try:
        with db.engine.begin() as conn:
            result = conn.execute(sqlalchemy.text("""SELECT comment_id
                                            FROM comments 
                                            where comment_id = :id
                                        """), 
                                        [{"id": id}]).one_or_none()
            if result is None:
                raise HTTPException(status_code=404, 
                        detail=("comment_id does not exist in comments table."))

            conn.execute(sqlalchemy.text("""DELETE 
                                        FROM comments 
                                        where comment_id = :id"""), 
                                        [{"id": id}])

        return f"comment_id deleted: {id}"
    
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise