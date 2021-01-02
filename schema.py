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
    open = Column(FLOAT)
    change = Column(FLOAT)

    def __init__(self, id, date, high, low, close, volume, open, change):
        self.id = id
        self.date = date
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.open = open
        self.change = change

class Analysis(Base):

    __tablename__ = 'analysis'

    id = Column(INT, primary_key=True)
    amplitude = Column(FLOAT)
    ma_5 = Column(FLOAT)
    ma_20 = Column(FLOAT)
    ma_60 = Column(FLOAT)
    ma_120 = Column(FLOAT)
    ma_240 = Column(FLOAT)
    volume = Column(FLOAT)
    trend = Column(INT)
    classify = Column(INT)

    def __init__(self, id, amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, trend, classify=-1):
        self.id = id
        self.amplitude = amplitude
        self.ma_5 = ma_5
        self.ma_20 = ma_20
        self.ma_60 = ma_60
        self.ma_120 = ma_120
        self.ma_240 = ma_240
        self.volume = volume
        self.trend = trend
        self.classify = classify
    
    def setClassify(self, classify): 
        self.classify = classify
    