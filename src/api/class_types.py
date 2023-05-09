from fastapi import APIRouter
from src import database as db
import sqlalchemy

router = APIRouter()

@router.get("/class-types/", tags=["class_types"])
def get_class_types():
    """
    This endpoint returns all of the types of training classes in the database. 
    For every type, it returns:
        `type_id`: the id associated with the class type
        `type`: the type of class
        `description`: a description of the class
        `max_num_dogs`: number of dogs that can be in class type
    """
    stmt = sqlalchemy.text("""                            
        SELECT class_type_id, type, description, max_num_dogs
        FROM class_types              
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt)

        json = []
        for row in result:
            json.append(
                {
                    "type_id": row.class_type_id,
                    "type": row.type,
                    "description": row.description,
                    "max_num_dogs": row.max_num_dogs,
                }
            )

    return json