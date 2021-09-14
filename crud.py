from sqlalchemy.orm import Session

import models, schemas


def get_score(db: Session, token_id: int):
  return db.query(models.Score).filter(models.Score.tokenId == token_id).first()

def get_scores(db: Session):
    return db.query(models.Score).all()

def add_score(db: Session, token_id: int, score: float):
    db_item = models.Score(tokenId=token_id, score=score)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
