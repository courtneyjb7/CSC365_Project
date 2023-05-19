from fastapi import APIRouter
from src import database as db
import sqlalchemy
from fastapi.params import Query

router = APIRouter()

@router.get("/class-types/", tags=["class_types"])
def get_class_types(
    type: str = "", 
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0)):
    """
    This endpoint returns all of the types of training classes in the database. 
    For every type, it returns:
        `type_id`: the id associated with the class type
        `type`: the type of class
        `description`: a description of the class
        `max_num_dogs`: number of dogs that can be in class type

    You can filter by type with the `type` query parameter. 
    For example, "Puppy" or "Beginner".
    """
    stmt = sqlalchemy.text("""                            
        SELECT class_type_id, type, description, max_num_dogs
        FROM class_types  
        WHERE type ILIKE :type 
        OFFSET :offset         
        LIMIT :limit           
    """)

    with db.engine.connect() as conn:
        result = conn.execute(stmt, [{"type": f"%{type}%",
                                      "offset": offset,
                                      "limit": limit}])

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