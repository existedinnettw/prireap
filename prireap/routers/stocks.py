from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, crud, models
from ..dependencies import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    # responses={404: {"description": "Not found"}},
)

# @router.get(

