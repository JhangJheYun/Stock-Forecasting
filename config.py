from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.getenv('DB_URL')
engine = create_engine(DB_URL)
Session : Session = sessionmaker(bind = engine)()
