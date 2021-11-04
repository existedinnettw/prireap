# import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
# numeric type contain decimal in sql
from sqlalchemy import Column, Integer, String, Enum, Numeric, DateTime, Sequence  # , Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, backref, validates, sessionmaker
from .database import Base, SessionLocal, engine

'''
TODO:
    may need alembic for migration
'''

load_dotenv()
# print(os.getenv('DBHOST'))


class Exchange(Base):
    '''
    code_name: e.g. TPE
    * crontab:
        although crontab is accept to be null, it is highly recommend to be filled to simplify program use.
        the datetime is base on UTC (without timezone).
        can add validates
    '''
    __tablename__ = 'exchange'
    id = Column(Integer, Sequence('exg_id_seq'), primary_key=True)
    name = Column(String, nullable=False, unique=True)
    code_name = Column(String, nullable=False, unique=True)
    strt_cron_utc = Column(String, nullable=True)
    end_cron_utc = Column(String, nullable=True)

    stocks = relationship("Stock", back_populates="exchange")

    @validates('code_name')
    def convert_upper(self, key, value):
        return value.upper()


class Stock(Base):
    '''
    symbol: 2330, GOOGL, APPL
    name: 台積電, 精英, apple inc
    '''
    __tablename__ = 'stock'
    id = Column(Integer, Sequence('stock_id_seq'), primary_key=True)
    symbol = Column(String, nullable=False)  # e.g. 2330, GOOGL
    name = Column(String, nullable=True)
    exchange_id = Column(Integer, ForeignKey(
        'exchange.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    exchange = relationship("Exchange", back_populates="stocks")
    # adr parent id
    UniqueConstraint('symbol', 'exchange_id', name='uq_sym_exg')


class StockKMin(Base):
    __tablename__ = 'stock_k_min'
    id = Column(Integer, Sequence('kmin_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    # interval = Column(Integer, nullable=False )
    open = Column(Numeric(scale=2), nullable=True)
    high = Column(Numeric(scale=2), nullable=True)
    low = Column(Numeric(scale=2), nullable=True)
    close = Column(Numeric(scale=2), nullable=True)
    volume = Column(Integer, nullable=True)
    transaction = Column(Integer, nullable=True) #transaction
    dividends = Column(Integer, nullable=True)
    stock_splits = Column(Integer, nullable=True)
    UniqueConstraint('stock_id', 'start_ts', name='uq_stk_ts')


class StockKHour(Base):
    __tablename__ = 'stock_k_hr'
    id = Column(Integer, Sequence('khr_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    # interval = Column(Integer, nullable=False )
    open = Column(Numeric(scale=2), nullable=True)
    high = Column(Numeric(scale=2), nullable=True)
    low = Column(Numeric(scale=2), nullable=True)
    close = Column(Numeric(scale=2), nullable=True)
    volume = Column(Integer, nullable=True)
    transaction = Column(Integer, nullable=True)
    dividends = Column(Integer, nullable=True)
    stock_splits = Column(Integer, nullable=True)
    UniqueConstraint('stock_id', 'start_ts', name='uq_stk_ts')


class StockKDay(Base):
    __tablename__ = 'stock_k_day'
    id = Column(Integer, Sequence('kday_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey(
        'stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    # interval = Column(Integer, nullable=False )
    open = Column(Numeric(scale=2), nullable=True)
    high = Column(Numeric(scale=2), nullable=True)
    low = Column(Numeric(scale=2), nullable=True)
    close = Column(Numeric(scale=2), nullable=True)
    volume = Column(Integer, nullable=True)
    transaction = Column(Integer, nullable=True)
    dividends = Column(Integer, nullable=True)
    stock_splits = Column(Integer, nullable=True)
    UniqueConstraint('stock_id', 'start_ts', name='uq_stk_ts')


if __name__ == '__main__':

    # # drop table if exist
    # Base.metadata.drop_all(engine, tables=[
    #                        Exchange.__table__, Stock.__table__, StockKMin.__table__, StockKHour.__table__, StockKDay.__table__], checkfirst=True)
    Base.metadata.create_all(bind=engine, checkfirst=True)  # create table


    with SessionLocal() as session:
        # insert
        session.add(Exchange(name='台灣證券交易所', code_name='TPE'))
        session.add(Stock(exchange_id=1, symbol='2330', name='台積電'))
        session.commit()

        rows = session.query(Exchange)
        # row=rows[0]
        # print(row.fee ,row.loan)
        print(rows)

        for row in rows:
            print(row.id, row.name, row.code_name)
            # print(row.product_id, row.deal_dt, row.price, row.qty, row.trade_type, row.total_price)

        # #kbar test
        # session.add(StockKMin(stock_id=1,
        #                 start_ts="2021-10-21T23:01:12.560Z",
        #                 volume=33,
        #                 open=800,
        #                 high=804,
        #                 low=799,
        #                 close=800,
        #                 dividends=5,
        #                 stock_splits=0))
        # session.commit()
        # rows = session.query(StockKMin)
        # for row in rows:
        #     print(row.id, row.stock_id, row.volume, row.high)
