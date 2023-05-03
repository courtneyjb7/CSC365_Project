# Technical Specification

## User Stories

As a trainer, I want to be the only one who is able to view and update my schedule.

As a trainer, when setting my schedule, I want to be able to select a type of class and set the time I will be teaching it. 

As a trainer, there are one or more types of classes that I can teach.

As a trainer, when I have to cancel a class, I want emails to be sent to the clients that were planning to attend, and money to be refunded.

As a trainer, I want to be able to view important information about a dog attending my class, and update notes on the dog’s progress.

As a dog owner/customer, I do not have access to these endpoints because the API is made for the dog trainers.

## Endpoints

GET /trainer/{trainer_id}
```
This endpoint can return and update a trainer by its identifiers. For each trainer, it returns:
  `trainer_id`: the id associated with the trainer
  `name`: name of the trainer
  `email`: the company email of the trainer
  `schedule_id`: the id of the trainer's schedule
  `schedule`: a dictionary of days (of datatype DATE), each mapped to a list of IDs of classes the trainer is holding that day
	{	
	  DATE: [class_id, class_id, …],
	}
```
POST /classes/
```
This endpoint adds a new class to a trainer's schedule.
  `date`: the day the class takes place, of datatype DATE
  `start_time`: the time the class starts
  `end_time`: the time the class ends
  `max_num_dogs`: the maximum amount of dogs that are allowed to attend
  `class_type_id`:the id of the type of class 
```
GET /classes/
```
This endpoint returns all the training classes in the database. For every class, it returns:
  `class_id`: the id associated with the class
  `trainer_id`: the id of the trainer teaching the class
  `type`: the type of class
  `date`: the date the class take places
  `num_of_dogs`: the number of dogs attending the class

You can filter by type by using the query parameter `type`
```
GET /classes/{class_id}
```
This endpoint returns a specific class in the database. For every class, it returns:
  `class_id`: the id associated with the trainer
  `type`: the type of the class
  `description`: description of the class
  `trainer_id`: name of the trainer
  `date`: the day the class takes place
  `start_time`: the time the class starts
  `end_time`: the time the class ends
  `dogs_attending`: a list of dog_ids for the dogs signed up for the class
  `dogs_attended`: a list of dog_ids for the dogs that showed up, or null if the class has not taken place
```
DELETE /classes/{class id}
```
This endpoint deletes a class based on its class ID.
```
GET /classes/{class_id}/dogs/
```
This endpoint returns all the dogs attending a specific class. For every dog, it returns:
  `dog_id`: the id associated with the dog
  `name`: the name of the dog
  `client_email`: the email of the owner of the dog
  `attended`: boolean indicating if the dog attended, or null if the class has not taken place
```
PUT /classes/{class_id}/{dog_id}/attendance
```
This endpoint sets a dog's attendance to a specific class to true or false.
  `attendance`: boolean indicating if the dog attended
```
GET /dogs/{dog_id}
```
This endpoint returns information about a dog in the database. For every dog, it returns:
  `dog_id`: the id associated with the dog
  `name`: the name of the dog
  `client_email`: the email of the owner of the dog
  `age`: the dog’s age
  `breed`: the dog’s breed
  `previous_classes`: a list of class_ids of classes the dog has taken
  `future_classes`: a list of class_ids of classes the dog is signed up for
  `owner_comments`: a string of information from the owner about the dog, 
  		    such as the dog’s allergies, possible aggression issues, etc.  (optional)
  `trainer_comments`: a string of comments from the trainer about the dog’s progress (optional)
```
POST /dogs/{dog_id}/comments
```
This endpoint updates trainer comments for a dog. 
  `trainer_comments`: a string to append to the existing comments from the trainer about the dog’s progress
```
GET /class-types/
```
This endpoint returns all of the types of training classes in the database. For every type, it returns:
  `type_id`: the id associated with the class type
  `type`: the type of class
  `description`: a description of the class
```
## Edge cases and transaction flows

If a dog does not attend a class, we will send an email reminder to the dog owner’s email.

If it is necessary to remove a dog from a class, for example, if the owner called to cancel, a trainer can remove them from the class.

If an owner changes their email information, then it will be updated in the dog’s information.

If a trainer cancels a class, an email is sent to each dog owner that was planning to attend.

If a trainer adds a class, its date and time are checked with all the other classes in the database. If the time conflicts with another class, 
an HTTPException is returned and the class cannot be added.  

If a trainer attempts to access a class, dog, schedule, etc. with an ID that does not exist, an HTTPException is returned.

If a trainer attempts to access a schedule or other trainer information that does not belong to them, it will result in an HTTPException.
