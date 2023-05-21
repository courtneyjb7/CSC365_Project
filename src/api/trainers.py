from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy
from fastapi.params import Query
from pydantic import BaseModel

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
        raise HTTPException(status_code=400, detail="password must be 6 or more characters.")
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
            """)
            conn.execute(stm, [
                {
                    "first": trainer.first_name,
                    "last": trainer.last_name,
                    "email": trainer.email,
                    "pwd": trainer.password
                }
            ])

            return "success"
    except Exception as error:
        print(f"Error returned: <<<{error}>>>")


@router.get("/trainers/{trainer_email}/{pwd}", tags=["trainers"])
def verify_password(trainer_email: str, pwd: str):
    """
    This endpoint verifies the login credentials for a trainer. 
    - `trainer_email`: the email associated with the trainer
    - `pwd`: trainer's password
    """

    check_valid = sqlalchemy.text(
                    """SELECT trainer_id 
                        FROM trainers
                        WHERE email = :email 
                        AND password = crypt(:pwd, password)""")
    
    with db.engine.begin() as conn:
        result = conn.execute(check_valid, [
            {"email": trainer_email,
             "pwd": pwd}
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