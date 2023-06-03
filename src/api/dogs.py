from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
from pydantic import BaseModel
from fastapi.params import Query

router = APIRouter()


@router.get("/dogs/{dog_id}", tags=["dogs"])
def get_dog(dog_id: int):
    """
    This endpoint returns information about a dog in the database. 
    For every dog, it returns:
    - `dog_id`: the id associated with the dog
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

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"id": dog_id}])
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
            "trainer_comments": []
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
    
    return json


class CommentJson(BaseModel):
    trainer_id: int
    comment_text: str


@router.post("/dogs/{dog_id}/comments", tags=["dogs"])
def add_comments(dog_id: int, new_comment: CommentJson):
    """
    This endpoint updates trainer comments for a dog. 
    - `dog_id`: the id of the dog the comment is about

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
                "dog_id": dog_id,
                "trainer_id": db.try_parse(int, new_comment.trainer_id), 
                "text": new_comment.comment_text
            }]).scalar_one()

        return "comments_id added: " + comment_id 
    
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
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
):
    """
    This endpoint returns all the dogs in the database. 
    For every dog, it returns:
    - `dog_id`: the id associated with the dog
    - `dog_name`: the name of the dog
    """

    stmt = sqlalchemy.text("""                            
        SELECT dog_id, dog_name
        FROM dogs 
        WHERE dog_name ILIKE :name
        OFFSET :offset         
        LIMIT :limit            
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"name": f"%{name}%",
                                      "offset": offset,
                                      "limit": limit}])
        json = []
        for row in result:
            json.append(
                {
                    "dog_id": row.dog_id,
                    "name": row.dog_name 
                }
            )

    return json


@router.delete("/dogs/comments/{comment_id}", tags=["dogs"])
def delete_comments(comment_id: int):
    """
    This endpoint deletes a comment for a dog based on its comment ID.
    """
    try:
        with db.engine.begin() as conn:
            result = conn.execute(sqlalchemy.text("""SELECT comment_id
                                            FROM comments 
                                            where comment_id = :id
                                        """), 
                                        [{"id": comment_id}]).one_or_none()
            if result is None:
                raise HTTPException(status_code=404, 
                        detail=("comment_id does not exist in comments table."))

            conn.execute(sqlalchemy.text("""DELETE 
                                        FROM comments 
                                        where comment_id = :id"""), 
                                        [{"id": comment_id}])

        return "success"
    
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise