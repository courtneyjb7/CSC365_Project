from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
from fastapi.params import Query
from pydantic import BaseModel
import re

router = APIRouter()

class TrainerJson(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

@router.post("/trainers/", tags=["trainers"])
def add_trainer(trainer: TrainerJson):
    """
    This endpoint adds a new trainer to the database. 
    - `first_name`: first name of the trainer
    - `last_name`: last name of the trainer
    - `email`: the company email of the trainer
    - `password`: the trainer's password. Password should be 6 characters or more.
    """
    if len(trainer.password) < 6:
        raise HTTPException(status_code=400, 
                            detail="password must be 6 or more characters.")
    

    if not re.search("^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$", trainer.email):
        raise HTTPException(status_code=400, 
                            detail="invalid email")

    try:
        with db.engine.begin() as conn:
            stm = sqlalchemy.text("""
                INSERT INTO trainers 
                (first_name, last_name, email, password) 
                VALUES (
                    :first,
                    :last,
                    :email,
                    crypt(:pwd, gen_salt('bf'))
                )
                RETURNING trainer_id
            """)
            trainer_id = conn.execute(stm, [
                {
                    "first": trainer.first_name,
                    "last": trainer.last_name,
                    "email": trainer.email,
                    "pwd": trainer.password
                }
            ]).scalar_one()

            return trainer_id
    except Exception as error:
        if error.args != ():
            details = (error.args)[0]
            if "DETAIL:  " in details:
                details = details.split("DETAIL:  ")[1].replace("\n", "")
            raise HTTPException(status_code=404, detail=details)
        else:
            raise


class TrainerCheck(BaseModel):
    trainer_email: str
    pwd: str

@router.post("/trainers/login/", tags=["trainers"])
def verify_password(trainer: TrainerCheck):
    """
    This endpoint verifies the login credentials for a trainer. Returns trainer id
    - `trainer_email`: the email associated with the trainer
    - `pwd`: trainer's password
    """

    check_valid = sqlalchemy.text(
                    """SELECT trainer_id 
                        FROM trainers
                        WHERE email ILIKE :email 
                        AND password = crypt(:pwd, password)""")
    
    with db.engine.begin() as conn:
        result = conn.execute(check_valid, [
            {"email": trainer.trainer_email,
             "pwd": trainer.pwd}
             ]).one_or_none()
        
        if result is None:
            raise HTTPException(status_code=404, detail="credentials not found")
        else:
            return result.trainer_id


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
    email: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)
):
    """
    This endpoint returns all the trainers in the database. 
    For every trainer, it returns:
    - `trainer_id`: the id associated with the trainer
    - `name`: full name of the trainer
    - `email`: the trainer's email

    You can set a limit and offset.
    You can filter by trainer email. 
    """

    stmt = sqlalchemy.text("""                            
        SELECT trainer_id, first_name, last_name, email
        FROM trainers  
        WHERE email ILIKE :email
        LIMIT :limit
        OFFSET :offset           
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"offset": offset,
                                      "limit": limit, 
                                      "email": f"%{email}%"}])
        json = []
        for row in result:
            json.append(
                {
                    "trainer_id": row.trainer_id,
                    "name": row.first_name + " " + row.last_name ,
                    "email": row.email
                }
            )

    return json