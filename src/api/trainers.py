from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
from fastapi.params import Query

router = APIRouter()

# @router.get("/trainers/", tags=["trainers"])
# def get_trainer(trainer_id: int):
#     """
#     This endpoint can return and update a trainer by its identifiers. 
#     For each trainer, it returns:
#     - `trainer_id`: the id associated with the trainer
#     - `first`: first name of the trainer
#     - `last`: last name of the trainer
#     - `email`: the company email of the trainer
#     """


# @router.get("/trainers/{trainer_id}", tags=["trainers"])
# def get_trainer(trainer_id: int):
#     """
#     This endpoint can return and update a trainer by its identifiers. 
#     For each trainer, it returns:
#     - `trainer_id`: the id associated with the trainer
#     - `first`: first name of the trainer
#     - `last`: last name of the trainer
#     - `email`: the company email of the trainer
#     """


@router.get("/trainers/{trainer_id}", tags=["trainers"])
def get_trainer(trainer_id: int):
    """
    This endpoint can return and update a trainer by its identifiers. 
    For each trainer, it returns:
    - `trainer_id`: the id associated with the trainer
    - `first`: first name of the trainer
    - `last`: last name of the trainer
    - `email`: the company email of the trainer
    """
    stmt = sqlalchemy.text("""                            
            SELECT trainer_id, first_name, last_name, email
            FROM trainers
            WHERE trainers.trainer_id = (:id)                        
        """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"id": trainer_id}])
        json = []
        for row in result:
            json.append(
                {
                    "trainer_id": row.trainer_id,
                    "first": row.first_name,
                    "last": row.last_name,
                    "email": row.email
                }
            )
    if json != []:
        return json
    
    raise HTTPException(status_code=404, detail="trainer not found.")


@router.get("/trainers/", tags=["trainers"])
def get_trainers(
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
):
    """
    This endpoint returns all the trainers in the database. 
    For every trainer, it returns:
    - `trainer_id`: the id associated with the trainer
    - `name`: full name of the trainer
    """

    stmt = sqlalchemy.text("""                            
        SELECT trainer_id, first_name, last_name
        FROM trainers  
        LIMIT :limit
        OFFSET :offset           
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"offset": offset,
                                      "limit": limit}])
        json = []
        for row in result:
            json.append(
                {
                    "trainer_id": row.trainer_id,
                    "name": row.first_name + " " + row.last_name 
                }
            )

    return json