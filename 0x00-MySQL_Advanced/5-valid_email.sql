-- this will create a trigger to resets valid_email if the email is changed
DELIMITER $$ 
CREATE TRIGGER email_trigger
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
IF NEW.email <> OLD.email
THEN
    SET NEW.valid_email = 0;
END IF;
END
$$
DELIMITER ;
