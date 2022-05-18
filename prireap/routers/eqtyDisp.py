from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import JSONResponse, Response
from .. import schemas, crud, models
from typing import List, Optional, Any, Union
from ..dependencies import get_db
import orjson
from sqlalchemy.orm import Session
from .. import schemas, crud, models, rawCrud
from datetime import datetime, date
from .util import ORJSONResponse, JSONDataResponse

router = APIRouter(
    tags=["institutional"],
    # responses={404: {"description": "Not found"}},
)


@router.get(
    "/eqty_disp/",
    # response_model=List[schemas.StockKBar]
    # response_class=ORJSONResponse
    description=r"""
        'from_d':'2020-11-01',
        'to_d':'2021-11-01,
        'stock_ids':[1,2]"""
)
def get_eqty_disps(
        from_d: Optional[Union[datetime,date]] = Query(None),
        to_d: Optional[Union[datetime,date]] = Query(None),
        stock_ids: List[Optional[int]] = Query(None),
        db: Session = Depends(get_db)):
    '''
    搭配query parameter 很有用
    stock_ids: array?
    '''
    list_of_dicts = rawCrud.get_eqty_disps_with_filter(
        db, start=from_d, stock_ids=stock_ids, end=to_d)
    return ORJSONResponse(list_of_dicts)


@router.post(
    "/eqty_disp/",
    response_model=schemas.EqtyDisp
)
def create_eqty_disp(
        obj_create: schemas.EqtyDispCreate,
        db: Session = Depends(get_db)
):
    db_stock = crud.get_stock(db, obj_create.stock_id)
    if not db_stock:
        raise HTTPException(
            status_code=404, detail="stock not exist, create stock first")

    db_kbar = crud.get_eqty_disp_by_stock_and_date(
        db, stock_id=obj_create.stock_id, date=obj_create.date)
    if db_kbar:
        raise HTTPException(status_code=400, detail="element already exist in db")
    # print(obj_create.high, obj_create.low, '\n\n\n')
    return crud.create_eqty_disp(db=db, obj=obj_create)


@router.post(
    "/composite/eqty_disp/",
    response_model=List[schemas.EqtyDisp]
)
def create_eqty_disps(eqty_disp_creates: List[schemas.EqtyDispCreate], db: Session = Depends(get_db)):
    '''
    * 只要有一個record duplicate，全部都取消
    TODO:
    要不要部份接受？dividends的有無資料的時間不太固定。
    '''
    for i in eqty_disp_creates:
        db_stock = crud.get_stock(db, i.stock_id)
        if not db_stock:
            raise HTTPException(
                status_code=404, detail="stock not exist, create stock first")

    # 要確定pass in 的本身有無重複，其中start_ts是datetime
    # print('check repeat in request body')
    create_simp = [str(i.stock_id)+i.date.isoformat()
                   for i in eqty_disp_creates]
    if len(eqty_disp_creates) != len(set(create_simp)):
        raise HTTPException(
            status_code=400, detail="duplicate in request list.")
    # print('list duplicate in db')  # this process stuck
    dupli_kdays = crud.list_eqty_disp_dupli(db=db, objs=eqty_disp_creates)
    if dupli_kdays:
        # 要不要直接create沒有重複的？
        raise HTTPException(
            status_code=400, detail="following kdays already exist {}.".format(dupli_kdays))
    # print(obj_create.high, obj_create.low, '\n\n\n')
    print('creating')
    return crud.create_eqty_disps(db=db, objs=eqty_disp_creates)
    # for i in eqty_disp_creates:
    #     #這個方法如果中間有問題e.g.重複，前面的會直接先insert
    #     create_kbar(db=db, obj_create=i)
