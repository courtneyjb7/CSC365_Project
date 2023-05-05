from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query
import sqlalchemy

router = APIRouter()


@router.get("/trainers/{trainer_id}", tags=["trainers"])
def get_trainer(trainer_id: int):
    """
    This endpoint can return and update a trainer by its identifiers. For each trainer, it returns:
        `trainer_id`: the id associated with the trainer
        `first`: first name of the trainer
        `last`: last name of the trainer
        `email`: the company email of the trainer
    """
    stmt = sqlalchemy.text("""                            
            SELECT *
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
