from pydantic import BaseModel

class Score(BaseModel):
    tokenId: int
    score: float
    
    class Config:
      orm_mode = True