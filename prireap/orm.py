# import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
# numeric type contain decimal in sql
from sqlalchemy import Column, Integer, String, Enum, Numeric, DateTime, Sequence  # , Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


load_dotenv()
# print(os.getenv('DBHOST'))


class Exchange(Base):
    __tablename__ = 'exchange'
    id = Column(Integer, Sequence('exg_id_seq'), primary_key=True)
    name = Column(String, nullable=False)
    code_name = Column(String, nullable=False, unique=True)


class Stock(Base):
    __tablename__ = 'stock'
    id = Column(Integer, Sequence('stock_id_seq'), primary_key=True)
    symbol = Column(String, nullable=False)  # e.g. 2330, GOOGL
    exchange_id = Column(Integer, ForeignKey('exchange.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    # adr parent id
    UniqueConstraint('symbol', 'exchange_id', name='uq_sym_exg')


class StockKMin(Base):
    __tablename__ = 'stock_k_min'
    id = Column(Integer, Sequence('kmin_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey('stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    # interval = Column(Integer, nullable=False )
    volume = Column(Integer, nullable=False)
    turnover = Column(Integer, nullable=False)
    open = Column(Numeric(precision=2), nullable=False)
    high = Column(Numeric(precision=2), nullable=False)
    low = Column(Numeric(precision=2), nullable=False)
    close = Column(Numeric(precision=2), nullable=False)
    n_deals = Column(Integer, nullable=True)  # api may not have such data
    dividends = Column(Integer, nullable=True)
    stock_splits = Column(Integer, nullable=True)
    UniqueConstraint('stock_id', 'start_ts', name='uq_stk_ts')


class StockKHour(Base):
    __tablename__ = 'stock_k_hr'
    id = Column(Integer, Sequence('khr_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey('stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    # interval = Column(Integer, nullable=False )
    volume = Column(Integer, nullable=False)
    turnover = Column(Integer, nullable=False)
    open = Column(Numeric(precision=2), nullable=False)
    high = Column(Numeric(precision=2), nullable=False)
    low = Column(Numeric(precision=2), nullable=False)
    close = Column(Numeric(precision=2), nullable=False)
    n_deals = Column(Integer, nullable=True)  # api may not have such data
    dividends = Column(Integer, nullable=True)
    stock_splits = Column(Integer, nullable=True)
    UniqueConstraint('stock_id', 'start_ts', name='uq_stk_ts')


class StockKDay(Base):
    __tablename__ = 'stock_k_day'
    id = Column(Integer, Sequence('kday_id_seq'), primary_key=True)
    stock_id = Column(Integer, ForeignKey('stock.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    start_ts = Column(DateTime, nullable=False)
    # interval = Column(Integer, nullable=False )
    volume = Column(Integer, nullable=False)
    turnover = Column(Integer, nullable=False)
    open = Column(Numeric(precision=2), nullable=False)
    high = Column(Numeric(precision=2), nullable=False)
    low = Column(Numeric(precision=2), nullable=False)
    close = Column(Numeric(precision=2), nullable=False)
    n_deals = Column(Integer, nullable=True)  # api may not have such data
    dividends = Column(Integer, nullable=True)
    stock_splits = Column(Integer, nullable=True)
    UniqueConstraint('stock_id', 'start_ts', name='uq_stk_ts')


if __name__ == '__main__':
    engine = create_engine( os.getenv('DB_URL') )  # link to market data db
    Session = sessionmaker(engine)
    session = Session()

    # drop table if exist
    Base.metadata.drop_all(engine, tables=[
                           Exchange.__table__, Stock.__table__, StockKMin.__table__, StockKHour.__table__, StockKDay.__table__], checkfirst=True)
    Base.metadata.create_all(engine)  # create table

    # insert
    session.add(Exchange(name='台灣證券交易所', code_name='TPE') )
    session.add(Stock(exchange_id=1, symbol='2330'))
    session.commit()

    rows = session.query(Exchange)
    # row=rows[0]
    # print(row.fee ,row.loan)
    print(rows)
    for row in rows:
        print(row.id,row.name,row.code_name)
        # print(row.product_id, row.deal_dt, row.price, row.qty, row.trade_type, row.total_price)
