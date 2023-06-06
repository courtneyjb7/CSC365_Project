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
    - `trainer_id`: the id associated with the trainer
    - `name`: full name of the trainer
    - `email`: the trainer's email

You can set a limit and offset.
You can filter by trainer email and/or name.
```
GET /trainers/{id}
```
This endpoint can return and update a trainer by its identifiers. 
For each trainer, it returns:
    - `trainer_id`: the id associated with the trainer
    - `first`: first name of the trainer
    - `last`: last name of the trainer
    - `email`: the company email of the trainer
```
POST /trainers/login/
```
This endpoint verifies the login credentials for a trainer. Returns trainer id
    - `trainer_email`: the email associated with the trainer
    - `pwd`: trainer's password
```
POST /trainers/
```
This endpoint adds a new trainer to the database. 
    - `first_name`: first name of the trainer
    - `last_name`: last name of the trainer
    - `email`: the company email of the trainer
    - `password`: the trainer's password. Password should be 6 characters or more.
```
GET /classes/
```
This endpoint finds classes that meet the given criteria. 
You can filter by trainer_id, class_type_id, a time range, and
days of the week. If a date is specified, only classes that 
occur on or after the date will be returned. 
It accepts a limit and is sorted by date in ascending order. 

For every class, it returns:
    - `class_id`: the id associated with the class
    - `trainer_id`: the id of the trainer
    - `trainer_name`: first and last name of the trainer
    - `type`: the type of class
    - `date`: the date the class takes place on
    - `start_time`: the time the class starts
    - `end_time`: the time the class ends
    - `room_id`: the id of the room the class takes place in
    - `num_of_dogs_attended`: the number of dogs attending the class
```
GET /classes/{id}
```
This endpoint returns a specific class in the database. For every class, it returns:
    - `class_id`: the id associated with the class
    - `type`: the type of the class
    - `description`: description of the class
    - `trainer_id`: the id of the trainer teaching the class
    - `trainer_first_name`: the first name of the trainer 
    - `trainer_last_name`: the first name of the trainer 
    - `date`: the day the class takes place
    - `start_time`: the time the class starts
    - `end_time`: the time the class ends
    - `room_id`: the id of the room the class takes place in
    - `room_name`: the name of the room the class takes place in
    - `dogs_attended`: a dictionary of a dog's id, name, and checkin time
                        for the dogs that attended
```
POST /classes/
```
This endpoint adds a new class to a trainer's schedule.
    - `trainer_id`: id of the trainer teaching the class
    - `date`: the day the class takes place, given by:
        • "yyyy-mm-dd": provide a string with the year, month, and day seperated by hyphen (-)
    - `start_time`: the time the class starts, given by:
        • "hh:mm AM/PM": provide a string with the hour and minutes seperated with a colon, as well as an indication whether time is AM or PM
    - `end_time`: the time the class ends, given by the following values:
        • "hh:mm AM/PM": provide a string with the hour and minutes seperated with a colon, as well as an indication whether time is AM or PM
    - `class_type_id`:the id of the type of class
    - `room_id`: the id of the room the trainer wants to teach the class in
```
POST /classes/{id}/attendance
```
This endpoint adds a dog's attendance to a specific class.
    - `attendance_id`: the id of the attendance record
    - `dog_id`: the id of the dog attending
    - `id`: the id of the class the dog is attending
```
DELETE /classes/{id}
```
This endpoint deletes a class based on its class ID.
```
GET /dogs/
```
This endpoint returns all the dogs in the database. 
For every dog, it returns:
    - `dog_id`: the id associated with the dog
    - `dog_name`: the name of the dog
    - `birthday`: the birthday of the dog
    - `breed`: the dog's breed
    - `client_email`: the email of the owner of the dog
```
GET /dogs/{id}
```
This endpoint returns information about a dog in the database. 
For every dog, it returns:
    - `id`: the id associated with the dog
    - `name`: the name of the dog
    - `client_email`: the email of the owner of the dog
    - `birthday`: the dog's date of birth
    - `breed`: the dog's breed
    - `trainer_comments`: a list of comments from the 
            trainer about the dog's progress 

Each comment returns:
    - `comment_id`: the id of the comment
    - `trainer`: the name of the trainer who wrote the comment
    - `time_added`: the day and time the comment was made
    - `text`: the comment text
```
POST /dogs/{dog_id}/comments
```
This endpoint updates trainer comments for a dog. 
    - `id`: the id of the dog the comment is about

Provide a body json with the following information:
    - `trainer_id`: the id of the trainer who made the comment
    - `comment_text`: a string from the trainer about the dog's progress
```
DELETE /dogs/comments/{id}
```
This endpoint deletes a comment for a dog based on its comment ID.
```
GET /class-types/
```
This endpoint returns all of the types of training classes in the database. 
For every type, it returns:
    - `type_id`: the id associated with the class type
    - `type`: the type of class
    - `description`: a description of the class
    - `max_num_dogs`: number of dogs that can be in class type
    
You can filter by type with the `type` query parameter. 
For example, "Puppy" or "Beginner".
```
GET /rooms/
```
This endpoint returns a room_id of a room in the facility that best meets the
criteria of a potential class to take place there. 
It returns the smallest room that is available at the given time and
has a max dog capacity greater than the given class type's
max number of dogs. If the only available rooms are smaller than the class type max,
it throws an error but says what the largest room available is.

Given:
    - `class type`: class you are interested in signing up a dog for
    - `date`: the day the class takes place, given by:
        - "yyyy-mm-dd": provide a string with the year, month, and day seperated by hyphen (-)
    - `start_time`: the time the class starts, given by:
        - "hh:mm AM/PM": provide a string with the hour and minutes seperated with a colon, 
        as well as an indication whether time is AM or PM
    - `end_time`: the time the class ends, given by:
        - "hh:mm AM/PM": provide a string with the hour and minutes seperated with a colon, 
        as well as an indication whether time is AM or PM
    it returns:
    - `room_id`: the id of the room in the facility that meets the class's needs
    - `room_name`: the name of the room
    - `max_dog_capacity`: the maximum number of dogs that can fit in the room
    - `max_class_size`: the max number of dogs that can attend a class of the given class type
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
