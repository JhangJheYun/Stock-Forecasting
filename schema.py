from sqlalchemy import INT, VARCHAR, DATE, FLOAT, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(Base):

    __tablename__ = 'stock'

    id = Column(INT, primary_key=True)
    name = Column(VARCHAR)

class History(Base):

    __tablename__ = 'history'

    id = Column(INT, primary_key=True)
    date = Column(DATE, primary_key=True)
    high = Column(FLOAT)
    low = Column(FLOAT)
    close = Column(FLOAT)
    volumn = Column(INT)