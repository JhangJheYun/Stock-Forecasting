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
    volume = Column(INT)

    def __init__(self, id, date, high, low, close, volume):
        self.id = id
        self.date = date
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

class Analysis(Base):

    __tablename__ = 'analysis'

    id = Column(INT, primary_key=True)
    