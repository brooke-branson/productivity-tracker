from sqlalchemy import select


def add_item(db, model):
    try:
        db.add(model)
        db.commit()
        db.refresh(model)

        return model

    except Exception:
        db.rollback()
        raise

def remove_item(db, model, id, response_model=None):
    existing_item = db.scalar(select(model).where(model.id == id))

    if not existing_item:
        return None

    deleted_item = response_model.model_validate(existing_item) if response_model else existing_item

    try:
        db.delete(existing_item)
        db.commit()

        return deleted_item
    except Exception:
        db.rollback()
        raise
    
def get_item(db, model, id, response_model=None):
    item = db.scalar(select(model).where(model.id == id))

    if not item:
        return None

    if response_model:
        return response_model.model_validate(item)
    else:
        return item