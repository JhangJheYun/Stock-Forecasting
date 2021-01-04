from configparser import ConfigParser


def config(filename='db.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
# import os

# load_dotenv()
# DB_URL = os.getenv('DB_URL')
# engine = create_engine(DB_URL)
# Session : Session = sessionmaker(bind = engine)()
