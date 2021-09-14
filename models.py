from sqlalchemy import Column, Integer, String, Float

from database import Base

class Score(Base):

    __tablename__ = "scores"

    tokenId = Column(Integer, primary_key=True, index=True)
    score = Column(Float, index=True)

    class Config:
      orm_mode = True

