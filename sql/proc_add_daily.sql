BEGIN;
CREATE OR REPLACE FUNCTION add_daily(in_duck_id varchar(128), in_message varchar(500)) RETURNS timestamp AS $$
DECLARE
    ts        timestamp;
    daily_day timestamp;
    last_pk   integer;
BEGIN

-- Figure out now and today
SELECT now() INTO ts;
SELECT date_trunc('day',(ts-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST') INTO daily_day;

-- Figure out if a daily already exists for today
SELECT daily_pk 
FROM dailies d 
JOIN users u ON d.user_fk=u.user_pk 
WHERE date_trunc('day',(create_dt-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST')=daily_day 
    AND u.duck_id=in_duck_id
LIMIT 1 INTO last_pk;

IF NOT FOUND THEN
    -- No existing daily for today
    INSERT INTO dailies (user_fk,create_dt,message) SELECT user_pk,ts,in_message FROM users WHERE duck_id=in_duck_id;
    RETURN daily_day;
END IF;

-- Working on an update rather than a new insertion
UPDATE dailies 
SET (create_dt,message)=(ts,in_message) 
FROM users 
WHERE user_pk=user_fk
    AND daily_pk=last_pk
    AND duck_id=in_duck_id
    AND date_trunc('day',(ts-interval '6 hours')::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'PST')=daily_day;
RETURN daily_day;

END;
$$ LANGUAGE plpgsql;
COMMIT;