# dog_trainer_api

Veronica Guzman (vguzma08@calpoly.edu)

Courtney Barber (cbarbe03@calpoly.edu)

### Project Description
For our project, we will create a database that contains information for a Dog Training and Boarding company. The database will be accessed by employees of the company. We will store data about the pet owner (contact information, number of pets, etc.) and the pet (name, breed, training progress, etc.). We will also have multiple training packages with their own pricing plan. The database will keep track of the trainers, including their availability, specialty, and wage. General information, such as inventory, will also be stored. 


[ER Diagram](Documentation/ER_Dog_Trainer_Diagram.pdf)

Vercel Links:
- Staging: https://dog-trainer-staging.vercel.app/
- Production: https://dog-trainer-api.vercel.app/

To rebuild alembic and populate with fake data, run:
```
sh populate_alembic.sh
```
