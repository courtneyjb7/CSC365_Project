# Technical Specification

## User Stories

As a trainer, I want to be the only one who is able to view and update my schedule.

As a trainer, when setting my schedule, I want to be able to select a type of class and set the time I will be teaching it. 

As a trainer, there are one or more types of classes that I can teach.

As a trainer, when I have to cancel a class, I want emails to be sent to the clients that were planning to attend, and money to be refunded.

As a trainer, I want to be able to view important information about a dog attending my class, and update notes on the dog’s progress.

As a dog owner/customer, I do not have access to these endpoints because the API is made for the dog trainers.

## Endpoints
GET /trainers/
```
This endpoint returns all the trainers in the database. 
For every trainer, it returns:
    `trainer_id`: the id associated with the trainer
    `name`: full name of the trainer
```
GET /trainers/{trainer_id}
```
This endpoint can return and update a trainer by its identifiers. 
For each trainer, it returns:
    `trainer_id`: the id associated with the trainer
    `first`: first name of the trainer
    `last`: last name of the trainer
    `email`: the company email of the trainer
```
POST /classes/{trainer_id}
```
This endpoint adds a new class to a trainer's schedule.
    `date`: the day the class takes place, given by the following three values:
        • "month": int representing month number of date
        • "day": int representing day number of date
        • "year": int representing year number of date
    `start_time`: the time the class starts, given by the following values:
        • "start_hour": int representing the hour of start_time
        • "start_minutes": int representing the minutes of start_time
    `end_time`: the time the class ends, given by the following values:
        • "end_hour": int representing the hour of end_time
        • "end_minutes": int representing the minutes of end_time
    `class_type_id`:the id of the type of class
```
GET /classes/
```
This endpoint returns all the training classes in the database. 
For every class, it returns:
    `class_id`: the id associated with the class
    `trainer_name`: name of the trainer
    `type`: the type of class
    `date`: the date the class take places
    `num_of_dogs_attended`: the number of dogs attending the class

    You can filter by type with the `type` query parameter.

    The `limit` and `offset` query parameters are used for pagination. 
        The `limit` query parameter specifies the maximum number 
        of results to return. 
        The `offset` query parameter specifies the
        number of results to skip before returning results.

    Classes are sorted by date in descending order.
```
GET /classes/{class_id}
```
This endpoint returns a specific class in the database. For every class, it returns:
    `class_id`: the id associated with the trainer
    `type`: the type of the class
    `description`: description of the class
    `trainer_first_name`: the first name of the trainer teaching the class
    `trainer_last_name`: the first name of the trainer teaching the class
    `date`: the day the class takes place
    `start_time`: the time the class starts
    `end_time`: the time the class ends
    `dogs_attended`: a dictionary of a dog's id, name, and checkin time for the dogs that attended
```
DELETE /classes/{class id}
```
This endpoint deletes a class based on its class ID.
```
PUT /classes/{class_id}/{dog_id}/attendance
```
This endpoint adds a dog's attendance to a specific class.
    `attendance_id`: the id of the attendance record
    `dog_id`: the id of the dog attending
    `class_id`: the id of the class the dog is attending
    `check_in`: the timestamp the dog checked in
        • "month": int representing month number of date
        • "day": int representing day number of date
        • "year": int representing year number of date
        • "hour": int representing the hour dog was checked in
        • "minutes": int representing the minutes dog was checked in
```
GET /dogs/
```
This endpoint returns all the dogs in the database. 
For every dog, it returns:
    `dog_id`: the id associated with the dog
    `dog_name`: the name of the dog
```
GET /dogs/{dog_id}
```
This endpoint returns information about a dog in the database. 
For every dog, it returns:
    `dog_id`: the id associated with the dog
    `name`: the name of the dog
    `client_email`: the email of the owner of the dog
    `birthday`: the dog's date of birth
    `breed`: the dog's breed
    `trainer_comments`: a list of comments from the 
        trainer about the dog's progress

        Each comment returns:
            `comment_id`: the id of the comment
            `trainer`: the name of the trainer who wrote the comment
            `time_added`: the day and time the comment was made
            `text`: the comment text
```
POST /dogs/{dog_id}/comments
```
This endpoint updates trainer comments for a dog. 
    `comment_id`: the id of the comment
    `dog_id`: the id of the dog the comment is about
    `trainer_id`: the id of the trainer who made the comment
    `comment_text`: a string from the trainer about the dog's progress
    `time_added`: the time and date the comment was made
```
GET /class-types/
```
This endpoint returns all of the types of training classes in the database. 
For every type, it returns:
    `type_id`: the id associated with the class type
    `type`: the type of class
    `description`: a description of the class
    `max_num_dogs`: number of dogs that can be in class type
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
