-- DROP INDEX dogs_idx;
-- DROP INDEX comments_idx ;
-- DROP INDEX classes_idx;
-- DROP INDEX class_attendance_idx;
-- CREATE INDEX dogs_idx ON dogs (dog_name text_pattern_ops, breed text_pattern_ops,  client_email text_pattern_ops, birthday, dog_id) ;
-- CREATE INDEX comments_idx ON comments (dog_id, trainer_id, time_added, comment_text, comment_id);
-- CREATE INDEX room_classes_idx ON classes (room_id, date, start_time, end_time);
-- CREATE INDEX classes_idx ON classes (date, start_time, end_time, trainer_id, class_type_id, room_id, class_id);
-- CREATE INDEX class_attendance_idx ON attendance (class_id, dog_id, check_in);
-- CREATE INDEX classes_attendance_idx ON attendance (class_id);




-- DROP INDEX dogs_idx
-- CREATE INDEX dogs_idx ON dogs (dog_name text_pattern_ops, breed text_pattern_ops,  client_email text_pattern_ops, birthday, dog_id) ;

-- EXPLAIN ANALYZE
-- SELECT dog_id, dog_name, birthday, breed, client_email
-- FROM dogs 
-- WHERE dog_name ILIKE 'Aaron%'
-- AND breed ILIKE 'Gold%'
-- AND client_email ILIKE 'a%'
-- OFFSET 1        
-- LIMIT 40



-- DROP INDEX dogs_idx
-- CREATE INDEX dogs_idx ON dogs (dog_name text_pattern_ops, breed text_pattern_ops,  client_email text_pattern_ops, birthday, dog_id) ;
-- CREATE INDEX comments_idx ON comments (dog_id, trainer_id, time_added, comment_text, comment_id)
-- CREATE INDEX trainers ON trainers (last_name, first_name, trainer_id)

-- EXPLAIN ANALYZE    
-- SELECT dogs.dog_id, dogs.dog_name, dogs.client_email, 
--     dogs.birthday, dogs.breed, comments.comment_id,
--     comments.time_added, comments.comment_text,
--     trainers.first_name, trainers.last_name
-- FROM dogs
-- LEFT JOIN comments on comments.dog_id = dogs.dog_id
-- LEFT JOIN trainers on comments.trainer_id = trainers.trainer_id
-- WHERE dogs.dog_id = 1
-- ORDER BY comments.time_added desc



-- DROP INDEX rooms_idx
-- CREATE INDEX rooms_idx ON rooms (room_id, room_name, max_dog_capacity) ;
-- CREATE INDEX classes_idx ON classes (room_id, date, start_time, end_time);

-- EXPLAIN ANALYZE
-- SELECT room_id, max_dog_capacity, room_name
-- FROM rooms
-- WHERE room_id NOT IN (
--     SELECT classes.room_id
--     FROM classes
--     JOIN rooms ON classes.room_id = rooms.room_id
--     WHERE classes.date = '2023-06-05' AND 
--         ((CAST('8:00:00 AM' AS TIME) < classes.start_time 
--             AND CAST('11:00:00 AM' AS TIME) > classes.start_time)
--         OR (CAST('8:00:00 AM' AS TIME) < classes.end_time 
--             AND CAST('11:00:00 AM' AS TIME) > classes.end_time))
-- )
-- ORDER BY max_dog_capacity ASC