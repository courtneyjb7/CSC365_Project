from fastapi import APIRouter

router = APIRouter()


@router.get("/trainer/{trainer_id}", tags=["trainers"])
def get_trainer(trainer_id: int):
    """
    This endpoint can return and update a trainer by its identifiers. 
    For each trainer, it returns:
        `trainer_id`: the id associated with the trainer
        `name`: name of the trainer
        `email`: the company email of the trainer
    """
    
    return "Trainer"