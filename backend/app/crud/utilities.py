from sqlalchemy import select


def add_item(db, model):
    try:
        db.add(model)
        db.commit()
        db.refresh(model)

        return model

    except Exception as e:
        db.rollback()
        raise e