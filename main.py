from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import re

from solver import solve

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

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.post("/api/solve")
async def do_solve(req: SolveRequest):
  try:
    sol = solve(req.hash)
  except ValueError as err:
    raise HTTPException(status_code=420, detail=f'Error solving cus i suck with math probably. From scipy.integrate.solve_ivp: {err}')

  return sol