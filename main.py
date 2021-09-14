from typing import Dict, List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import re

from solver import solve

from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)


class SolveRequest(BaseModel):
  hash: str

  @validator('hash')
  def hash_is_64hex(cls, v):
    p = re.compile(r'[^0-f]+')
    m = p.findall(v)
    if m:
      raise ValueError(f'provided hash contains invalid symbols {m}')
    
    if len(v) != 64:
      raise ValueError('hash length is not 64')

    return v

@app.post("/solve/")
async def do_solve(req: SolveRequest):
  try:
    sol = solve(req.hash)
  except ValueError as err:
    raise HTTPException(status_code=420, detail=f'Error solving cus i suck with math probably. From scipy.integrate.solve_ivp: {err}')

  return sol


@app.post("/scores/", response_model=schemas.Score)
def create_score(score: schemas.Score, db: Session=Depends(get_db)):
  db_score = crud.get_score(db, score.tokenId)
  if db_score:
    raise HTTPException(status_code=400, detail="tokenId already has scored added to database")
  return crud.add_score(db, score.tokenId, score.score)

@app.get("/scores/")
def read_scores(db: Session=Depends(get_db)):
  res = {}
  scores = crud.get_scores(db)
  for score in scores:
    res[score.tokenId] = score.score
  return JSONResponse(jsonable_encoder(res))