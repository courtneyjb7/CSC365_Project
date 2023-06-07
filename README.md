# Dog Trainer API

## Authors
Veronica Guzman (vguzma08@calpoly.edu)

Courtney Barber (cbarbe03@calpoly.edu)

<details open="open">
<summary>Table of Contents</summary>
<br>

- [About](#about)
- [Vercel Links](#vercel-links)
- [Documentation Files](#documentation-files)
- [Run API Local](#run-api-on-your-local-machine)
    - [Prerequisites](#prerequisites)
    - [Set up your local environment](#set-up-your-local-environment)
    - [Environment Variables](#environment-variables)
    - [Alembic and Faker data](#alembic-and-faker-data)
    - [Run the API](#run-the-api)
</details>

## About
This API simulates a dog training company's database for its trainers. The trainers can create an account and log in. They can access information about other trainers, classes taking place, class types, rooms in the facility, and dogs. Trainers can also create and schedule classes, check dogs into a class they are attending, and provide comments on the dog's progress. When scheduling a class, the trainers can check what rooms in the facility are available at the given time and date.  

## Vercel Links
We set up our API endpoints to run on vercel. Below are links to our production and staging API endpoints:
- Production: https://dog-trainer-api.vercel.app/
- Staging: https://dog-trainer-staging.vercel.app/

## Documentation Files
Listed below are documents we have gathered that provide further insight into the development of this API.

To view and read more about our API endpoints, check out our [Technical Specification](Documentation/Technical_Specification.pdf).

To organize our data, we developed an Entity Relationship Diagram that describes our data schema. Check out our [ER Diagram](Documentation/Dog_Trainer_ER_Diagram.pdf).

We identified the phenomenons that can occur from our top complex interactions of transactions in our database if we had no concurrency control and described our solution to ensure isolation of our transactions. Check out [Isolation Levels](Documentation/Isolation_Levels.pdf) to learn more.

To view the indexes we created to make our SQL execution time faster, check out [Indexes](Documentation/Indexes_dog_trainer_api.pdf).

## Run API on your local machine

### Prerequisites
All prerequisites are listed in [requirements.txt](requirements.txt)

### Set up your local environment
Follow steps listed [here](https://supabase.com/docs/guides/getting-started/local-development) in the Supabase documentation.

### Environment Variables
Create a .env file with these variables:
```
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_SERVER="localhost"
POSTGRES_PORT="54322"
POSTGRES_DB="postgres"
```

### Alembic and Faker data
To rebuild alembic and populate with fake data, run:
```
sh populate_alembic.sh
```

### Run the API
Run following on your terminal:
```
vercel dev
```

