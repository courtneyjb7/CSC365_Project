import os
import dotenv
import sqlalchemy


# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()

def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        raise Exception("Incorrect type")

## Postgres

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())
metadata_obj = sqlalchemy.MetaData()

trainers = sqlalchemy.Table("trainers", metadata_obj, autoload_with=engine)
dogs = sqlalchemy.Table("dogs", metadata_obj, autoload_with=engine)
comments = sqlalchemy.Table("comments", metadata_obj, autoload_with=engine)
classes = sqlalchemy.Table("classes", metadata_obj, autoload_with=engine)
class_types = sqlalchemy.Table("class_types", metadata_obj, autoload_with=engine)
attendance = sqlalchemy.Table("attendance", metadata_obj, autoload_with=engine)

