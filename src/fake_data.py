from faker import Faker
# import database as db
import sqlalchemy
import random
import os
import dotenv
from datetime import timedelta, datetime

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = sqlalchemy.create_engine(database_connection_url())

fake = Faker()
num_trainers = 20
num_class_types = 5 #fixed
num_rooms = 10 

num_dogs = 400000
num_attendances = 800000
num_classes = 400000
num_comments = 800000

def populate_trainers():
    
    with engine.begin() as conn:
        try:
            
            trainers = []
            for _ in range(num_trainers):      
                trainers.append({
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": fake.unique.email(domain="dogtrainers.com"),
                    "pwd": "password"
                })

            stm = sqlalchemy.text("""
                INSERT INTO trainers 
                (first_name, last_name, email, password) 
                VALUES (
                    :first_name,
                    :last_name,
                    :email,
                    crypt(:pwd, gen_salt('bf')) 
                )
            """)
            conn.execute(stm, trainers)
            
        except Exception as error:
            print(error)

def populate_dogs():
    
    breeds = ["Basset Hound", "Beagle", "Border Collie",
              "Dobermann", "Golden Retriever", "Chihuahua",
              "Maltese", "Rottweiler", "Pug", "Poodle"]
    
    with engine.begin() as conn:
        try:
            dogs = []
            for _ in range(num_dogs): 
                dogs.append({
                    "dog_name": fake.first_name(),
                    "client_email": fake.unique.email(),
                    "birthday": fake.date_of_birth(None, 1, 20),
                    "breed": random.choice(breeds) 
                })

            stm = sqlalchemy.text("""
                INSERT INTO dogs 
                (client_email, birthday, breed, dog_name) 
                VALUES (
                    :client_email,
                    :birthday,
                    :breed,
                    :dog_name
                )
            """)
            conn.execute(stm, dogs)
            
        except Exception as error:
            print(error)


def populate_class_types():
    with engine.begin() as conn:
        try:  
            class_types = [
                {
                    "type": "Puppy Training",
                    "description": "Potty training, puppy biting, barking, and basic commands will be covered.",
                    "max_num_dogs": 10
                },
                {
                    "type": "Beginner",
                    "description": "Dogs at the beginner level will learn basic manners and obedience techniques.",
                    "max_num_dogs": 10
                },
                {
                    "type": "Intermediate",
                    "description": "Dogs at the intermediate level will enhance their skills from previous classes.",
                    "max_num_dogs": 15
                },
                {
                    "type": "Advanced",
                    "description": "Dogs will learn more advanced skills and commands, including emotional support animal training.",
                    "max_num_dogs": 20
                },
                {
                    "type": "Dog Playdate",
                    "description": "A large group of dogs will interact and play together.",
                    "max_num_dogs": 50
                }
            ]

            stm = sqlalchemy.text("""
                INSERT INTO class_types 
                (type, description, max_num_dogs) 
                VALUES (
                    :type,
                    :description,
                    :max_num_dogs
                )
            """)
            conn.execute(stm, class_types)
            
        except Exception as error:
            print(error)

def populate_rooms():
    with engine.begin() as conn:
        rooms_lst = []
        for i in range(num_rooms):
            rooms_lst.append({
                "room_name": chr(65 + i),
                "max_dog_capacity": random.randint(10, 50)
            })
            
        try:  
            stm = sqlalchemy.text("""
                INSERT INTO rooms 
                (room_name, max_dog_capacity) 
                VALUES (
                    :room_name, 
                    :max_dog_capacity
                )
            """)
            conn.execute(stm, rooms_lst)
            
        except Exception as error:
            print(error)

def populate_attendance():
    with engine.begin() as conn:    
        try:
            attendances = []
            for _ in range(num_attendances): 
                attendances.append({
                    "dog_id": random.randint(1, num_dogs),
                    "class_id": random.randint(1, num_classes),
                    "check_in": fake.date_time_between()
                })

            stm = sqlalchemy.text("""
                INSERT INTO attendance
                (dog_id, class_id, check_in) 
                VALUES (
                    :dog_id,
                    :class_id,
                    :check_in
                )
            """)
            conn.execute(stm, attendances)
        
        except Exception as error:
            print(error)

def populate_classes():
    with engine.begin() as conn:
        try:
            
            classes = []
            for _ in range(num_classes):  
                # start_time = fake.time_object()
                s_time = datetime(2022, 1, 1, random.randint(0, 23), random.choice([0, 30]), 0)
                time_change = timedelta(hours=random.randint(1, 3))
                end_time = s_time + time_change

                classes.append({
                    "trainer_id": random.randint(1, num_trainers),
                    "date": fake.date_time_between(start_date='-20y', end_date='+3y'),
                    "start_time": s_time,#start_time,
                    "end_time": end_time,#start_time.timedelta(hours=1),
                    "class_type_id": random.randint(1, num_class_types),
                    "room_id": random.randint(1, num_rooms)
                })

            stm = sqlalchemy.text("""
                INSERT INTO classes
                (trainer_id, date, start_time, end_time, class_type_id, room_id) 
                VALUES (
                    :trainer_id, 
                    :date, 
                    :start_time, 
                    :end_time, 
                    :class_type_id, 
                    :room_id
                )
            """)
            conn.execute(stm, classes)
            
        except Exception as error:
            print(error)

def populate_comments():
    with engine.begin() as conn:    
        try:
            comments = []
            text_options = ["Much improvement",
                            "Learned many basic skills today!" ,
                            "Very well behaved dog!",
                            "Ready to move into a more advanced class",
                            "Still working on patience",
                            "Needs more training",
                            "Should attend the puppy class",
                            "Should move to the beginner class",
                            "Very energetic dog",
                            "Super calm dog",
                            "Belongs in the intermediate class",
                            "Will be ready to advance after next week",
                            "Work on the new skills learned today"]
            for _ in range(num_comments): 
                comments.append({
                    "dog_id": random.randint(1, num_dogs),
                    "trainer_id": random.randint(1, num_trainers),
                    "comment_text": random.choice(text_options),
                    "time_added": fake.date_time_between()
                })

            stm = sqlalchemy.text("""
                INSERT INTO comments
                (dog_id, trainer_id, comment_text, time_added) 
                VALUES (
                    :dog_id,
                    :trainer_id,
                    :comment_text,
                    :time_added
                )
            """)
            conn.execute(stm, comments)
        
        except Exception as error:
            print(error)

populate_trainers()     
populate_dogs()
populate_class_types()
populate_rooms()
populate_classes()
populate_attendance()
populate_comments()
