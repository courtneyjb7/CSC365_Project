# Technical Specification

## User Stories
As a trainer, I want to be able to be able to update my schedule.

As an employee, I want to be able to update and access individual information of a dog.

As an employee, I can’t change the dog_id number associated with a dog. I would only be able to get a new dog_id for a dog if I delete the existing data for the dog.

As a dog owner/customer, I cannot access this information.

As an employee, I want to have a secure account where I can login with a username and password. 

As an employee, I want to be able to update and access my customer’s contact and payment information. 


## Endpoints
**/trainer/**
```
This endpoint returns all the trainers in the database. For every trainer:
  `trainer_id`: the id associated with the trainer
  `name`: name of the trainer
```
**/trainer/*****{trainer_id}***
```
This endpoint can return and update a trainer by its identifiers. For each trainer:

  `trainer_id`: the id associated with the trainer
  `name`: name of the trainer
  `schedule`: a dictionary of days of the current week, each mapped to a list of IDs of classes the trainer is holding that day
    This is represented by:
      {	
        “day_of_week”: [class_id, class_id, …],
      }
```
**/dogs/**
```
This endpoint returns all the dogs in the database. For every dog:
  `dog_id`: the id associated with the dog
  `name`: the name of the dog
  `client_id`: the id of the owner of the dog
```
**/dogs/*****{dog_id}***
```
This endpoint returns all the dogs in the database. For every dog:
  `dog_id`: the id associated with the dog
  `name`: the name of the dog
  `client_id`: the id of the owner of the dog
  `age`: the dog’s age
  `breed`: the dog’s breed
  `classes`: a list of class_ids of classes the dog is signed up for
  `owner_comments`: a list of additional important information from the owner, 
                    such as the dog’s allergies, possible aggression issues, etc. 
```
**/client/**
```
This endpoint returns all the clients. For every client:
  `client_id`: the id associated with the client.
  `name`: name of the client
  `email`: client’s email
  `phone`: client’s phone
  `num_dogs`: number of dogs they have signed up
```
**/client/*****{client_id}***
```
This endpoint returns all the clients. For every client:
  `client_id`: the id associated with the client.
  `address`: the address the client has on file
  `email`: client’s email
  `phone`: client’s phone
  `payment`: payment type for client (cash or card)
  `dogs`: a list of all the dogs they have signed up in our system


For every dog in `dogs`:
  `dog_id`: the id associated with the dog
  `name`: name of dog
  `breed`: breed of dog
```
**/classes/**
```
This endpoint returns all the training classes in the database. For every class:
  `class_id`: the id associated with the class
  `trainer_id`: name of the trainer
  `date`: the day the class takes place
  `start_time`: the time the class starts
  `end_time`: the time the class ends
  `num_of_dogs`: the number of dogs attending the class
```
**/classes/*****{class_id}***
```
This endpoint returns a specific class in the database. For every class:
  `class_id`: the id associated with the trainer
  `trainer_id`: name of the trainer
  `date`: the day the class takes place
  `start_time`: the time the class starts
  `end_time`: the time the class ends
  `dogs_attending`: a list of dog_ids of the dogs attending the class
```


## Edge cases and transaction flows
A trainer may have to cancel their class last minute. If they find a replacement, the 
