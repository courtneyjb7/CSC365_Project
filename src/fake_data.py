from faker import Faker
# import database as db
import sqlalchemy
import random
import os
import dotenv

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
num_trainers = 2
num_dogs = 2
num_class_types = 5
num_rooms = 10


def populate_trainers():
    
    with engine.begin() as conn:
        try:
            for _ in range(num_trainers):      

                stm = sqlalchemy.text("""
                    INSERT INTO trainers 
                    (first_name, last_name, email, password) 
                    VALUES (
                        :first_name,
                        :last_name,
                        :email,
                        crypt(:pwd, gen_salt('bf')) 
                    ) RETURNING trainer_id
                """)
                trainer_id = conn.execute(stm, [{
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": fake.unique.email(domain="dogtrainers.com"),
                    "pwd": "password"#fake.password(length=10)
                }]).scalar_one()
                # print(trainer_id)
            
        except Exception as error:
            print(error)

def populate_dogs():
    
    breeds = ["Basset Hound", "Beagle", "Border Collie",
              "Dobermann", "Golden Retriever", "Chihuahua",
              "Maltese", "Rottweiler", "Pug", "Poodle"]
    with engine.begin() as conn:
        try:
            for _ in range(num_dogs):      

                stm = sqlalchemy.text("""
                    INSERT INTO dogs 
                    (client_email, birthday, breed, dog_name) 
                    VALUES (
                        :client_email,
                        :birthday,
                        :breed,
                        :dog_name 
                    ) RETURNING dog_id
                """)
                dog_id = conn.execute(stm, [{
                    "dog_name": fake.first_name(),
                    "client_email": fake.unique.email(),
                    "birthday": fake.date_of_birth(None, 1, 20),
                    "breed": random.choice(breeds)
                    
                }]).scalar_one()
                # print(dog_id)
            
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

populate_trainers()     
populate_dogs()
populate_class_types()
populate_rooms()
######################################################
# num_users = 200000
# posts_sample_distribution = np.random.default_rng().negative_binomial(0.04, 0.01, num_users)
# category_sample_distribution = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#                                                  num_users,
#                                                 p=[0.1, 0.05, 0.1, 0.3, 0.05, 0.05, 0.05, 0.05, 0.15, 0.1])
# total_posts = 0
# with engine.begin() as conn:
#     print("creating fake posters...")
#     posts = []
#     for i in range(num_users):
#         if (i % 10 == 0):
#             print(i)
        
#         profile = fake.profile()
#         username = fake.unique.email()
#         device_type = fake.random_element(elements=('Android', 'iOS', 'Web'))

#         poster_id = conn.execute(sqlalchemy.text("""
#         INSERT INTO users (username, full_name, birthday, device_type) VALUES (:username, :name, :birthday, :device_type) RETURNING id;
#         """), {"username": username, "name": profile['name'], "birthday": profile['birthdate'], "device_type": device_type}).scalar_one();

#         num_posts = posts_sample_distribution[i]
#         likes_sample_distribution = np.random.default_rng().negative_binomial(0.8, 0.0001, num_posts)  
#         for j in range(num_posts):
#             total_posts += 1
#             posts.append({
#                 "title": fake.sentence(),
#                 "content": fake.text(),
#                 "poster_id": poster_id,
#                 "category_id": category_sample_distribution[i].item(),
#                 "visible": fake.boolean(75),
#                 "created_at": fake.date_time_between(start_date='-5y', end_date='now', tzinfo=None),
#                 "likes": likes_sample_distribution[j].item(),
#                 "nsfw": fake.boolean(10)
#             })

#     if posts:
#         conn.execute(sqlalchemy.text("""
#         INSERT INTO posts (title, content, poster_id, category_id, visible, created_at) 
#         VALUES (:title, :content, :poster_id, :category_id, :visible, :created_at);
#         """), posts)

#     print("total posts: ", total_posts)
