

-- DROP PROCEDURE `scouting`.`insert_log`;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `insert_log`(IN p_message varchar(1000))
BEGIN
	 insert into logging (short_msg) values (p_message);
END$$
DELIMITER ;


-- DROP FUNCTION `scouting`.`get_tag`;
DELIMITER $$
CREATE FUNCTION `get_tag`(i integer, tag varchar(100)) RETURNS varchar(2000) READS SQL DATA
BEGIN
    declare v_json_key varchar(100);
    declare v_key varchar(2000);

	-- call insert_log(concat('get_tag: ', tag, ' - ', convert(i, CHAR)));
    
	set v_json_key = concat('$[', convert(i, CHAR), '].', tag);
    select JSON_EXTRACT(json_data, v_json_key) into v_key from staging;
    
    -- call insert_log(concat('returning: ', v_key));
    
    return v_key;
END$$
DELIMITER ;


-- DROP FUNCTION `scouting`.`strip_quotes`;
DELIMITER $$
CREATE FUNCTION `strip_quotes`(p_value varchar(1000)) RETURNS varchar(1000) READS SQL DATA
BEGIN
    declare v_value varchar(1000);

	set v_value = p_value;

	-- if the first character is a " then strip it
    if substr(v_value, 1, 1) = '"' then
		set v_value = substr(v_value, 2);
	end if;

	-- if the last character is a " then strip it
    if substr(v_value, -1, 1) = '"' then
		set v_value = substr(v_value, 1, char_length(v_value)-1);
	end if;
    
    return v_value;
END$$
DELIMITER ;


-- DROP FUNCTION `scouting`.`get_team`;
DELIMITER $$
CREATE FUNCTION `get_team`(i integer, tag varchar(100)) RETURNS int READS SQL DATA
BEGIN
    declare v_team_key varchar(100);
    declare v_team_id int;
	-- call insert_log(concat('getting team id: ', tag));
	
    -- get the team key for the i record and for the given tag (red1,red2,red3,blue1,blue2,blue3)
    set v_team_key = get_tag(i, tag);
	-- call insert_log(concat('got team key: ', ifnull(v_team_key,'NULL')));

	set v_team_key = strip_quotes(v_team_key);

	-- now get the system id for the team key
    select _id 
    into  v_team_id
    from team 
    where tba_team_key = v_team_key;
	-- call insert_log(concat('got team id: ', ifnull(v_team_id,'NULL')));
    
    return ifnull(v_team_id, -1);
END$$
DELIMITER ;

-- DROP PROCEDURE `scouting`.`load_team_match`;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `load_team_match`(p_team_id int, p_match_id int, p_alliance varchar(10), p_position int)
BEGIN    
    declare v_found integer;
    
    -- call insert_log(concat('loading team match for team: ', convert(p_team_id, CHAR)));
    
    IF p_team_id = -1 THEN
		call insert_log('ERROR: NO TEAM_ID... NO RECORD CREATED!!');
	ELSE
		
		-- now see if the record exists in the team match
		select count(*) 
		into v_found
		from team_match
		where team_id = p_team_id
		and   match_id = p_match_id;

		-- if it doesn't then insert a row
		if v_found = 0 then
			-- call insert_log('inserting...');

			INSERT INTO scouting.team_match (
				team_id,
				match_id,
				alliance,
				position,
				dq_yn)
			VALUES (
				p_team_id,
				p_match_id,
				p_alliance,
				p_position,
				'N');

			-- call insert_log('Team Match inserted...');
				
		-- it exists in the table so update it
		-- else
			-- call insert_log('Team Match updated ... NO ACTION!');
		end if;
	END IF;
END$$
DELIMITER ;

-- show procedure status like 'get_key_value';

-- DROP PROCEDURE `scouting`.`get_key_value`;
DELIMITER $$
CREATE PROCEDURE scouting.get_key_value(INOUT p_breakdown VARCHAR(4000), OUT p_key varchar(1000), OUT p_value varchar(1000)) 
BEGIN 
    declare	v_pos	int;

	set v_pos = instr(p_breakdown, ':');
    if v_pos = 0 then
		set p_breakdown = '';
	else
		set p_key = strip_quotes(trim(substr(p_breakdown, 1, v_pos-1)));
		set p_breakdown = substr(p_breakdown, v_pos+1);

		set v_pos = instr(p_breakdown, ',');
        if v_pos = 0 then
			set v_pos = instr(p_breakdown, '}');
		end if;
		set p_value = strip_quotes(trim(substr(p_breakdown, 1, v_pos-1)));
		set p_breakdown = trim(substr(p_breakdown, v_pos+1));
	end if;
END$$
DELIMITER ;

-- DROP PROCEDURE `scouting`.`load_breakdown`;
DELIMITER $$
CREATE PROCEDURE scouting.load_breakdown(p_match_id int, p_alliance varchar(10), p_score_breakdown varchar(4000))
BEGIN 
	declare	v_breakdown varchar(4000);
    declare v_key		varchar(2000);
    declare v_value		varchar(1000);
    declare	v_found		int;
    
	-- set a local variable and strip off the first character {
	set v_breakdown = substr(p_score_breakdown, 2);
    
    while (v_breakdown <> '') do
		call get_key_value(v_breakdown, v_key, v_value);
        
		select count(*) 
        into v_found
        from match_score
        where match_id = p_match_id
        and   alliance = p_alliance
        and   `key` = v_key;
        
        if v_found = 0 then
			INSERT INTO scouting.match_score (
				match_id,
				alliance,
				`key`,
				`value`)
			VALUES (
				p_match_id,
                p_alliance,
                v_key,
                v_value
			);
		else
			UPDATE scouting.match_score
            SET `value` = v_value
			where match_id = p_match_id
			and  alliance = p_alliance
			and   `key` = v_key;
		end if;
	end while;
END$$
DELIMITER ;


-- DROP PROCEDURE `scouting`.`load_matches`;
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `load_matches`()
BEGIN    
	declare v_count integer;
    declare i integer default 0;
    declare v_found integer;
    declare v_match_key varchar(1000);
    declare v_event_key varchar(1000);
    declare v_score_breakdown varchar(4000);
    declare v_match_id	int;
    declare v_event_id int;

	delete from logging where _id > 0;

	call insert_log('starting...');
	
    -- get the number of rows to process
	select json_length(json_data->>"$") 
    into v_count
    from staging;

	call insert_log(concat('Rows to process: ', convert(v_count, CHAR)));

	-- if we got data the get the event id ... it should be the same for all of them
    if v_count > 0 then
		set v_event_key = strip_quotes(get_tag(0, 'event_key'));
        call insert_log(concat('event_key: ', v_event_key));
        
        select _id
        into v_event_id
		from event 
        where tba_event_key = v_event_key; 
		call insert_log(concat('event_id: ', ifnull(convert(v_event_id, CHAR), 'NULL')));
    end if;
    
    -- loop through each row
    while i < v_count do
		set v_match_key = strip_quotes(get_tag(i, 'key'));
		call insert_log(concat(convert(i, CHAR), ' => processing: ', v_match_key));

		-- now see if the record exists
		select count(*) 
        into v_found
        from `match`
        where tba_match_key = v_match_key;
        
        -- if it doesn't then insert a row
        if v_found = 0 then
			-- call insert_log('inserting...');

				INSERT INTO `scouting`.`match`
				(
				`event_id`,
				`tba_match_key`,
				`comp_level`,
				`set_number`,
				`match_number`,
				`red_1_team_id`,
				`red_2_team_id`,
				`red_3_team_id`,
				`red_auto_score`,
				`red_teleop_score`,
				`red_adjust_points`,
				`red_total_score`,
				`red_foul_points`,
				`blue_1_team_id`,
				`blue_2_team_id`,
				`blue_3_team_id`,
				`blue_auto_score`,
				`blue_teleop_score`,
				`blue_adjust_points`,
				`blue_total_score`,
				`blue_foul_points`,
				`winner`)
				VALUES
				(
				v_event_id,
				v_match_key,
				strip_quotes(get_tag(i, 'comp_level')),
				get_tag(i, 'set_number'),
				get_tag(i, 'match_number'),
				get_team(i, 'alliances.red.team_keys[0]'),
				get_team(i, 'alliances.red.team_keys[1]'),
				get_team(i, 'alliances.red.team_keys[2]'),
				get_tag(i, 'score_breakdown.red.autoPoints'),
				get_tag(i, 'score_breakdown.red.teleopPoints'),
				get_tag(i, 'score_breakdown.red.adjustPoints'),
				get_tag(i, 'alliances.red.score'),
				get_tag(i, 'score_breakdown.red.foulPoints'),
				get_team(i, 'alliances.blue.team_keys[0]'),
				get_team(i, 'alliances.blue.team_keys[1]'),
				get_team(i, 'alliances.blue.team_keys[2]'),
				get_tag(i, 'score_breakdown.blue.autoPoints'),
				get_tag(i, 'score_breakdown.blue.teleopPoints'),
				get_tag(i, 'score_breakdown.blue.adjustPoints'),
				get_tag(i, 'alliances.blue.score'),
				get_tag(i, 'score_breakdown.blue.foulPoints'),
				strip_quotes(get_tag(i, 'winning_alliance')));
            
		-- it exists in the table so update it
		else
			-- call insert_log('updating...');

			UPDATE `scouting`.`match`
			SET	
				red_auto_score = get_tag(i, 'score_breakdown.red.autoPoints'),
				red_teleop_score = get_tag(i, 'score_breakdown.red.teleopPoints'),
				red_adjust_points = get_tag(i, 'score_breakdown.red.adjustPoints'),
				red_total_score = get_tag(i, 'alliances.red.score'),
				red_foul_points = get_tag(i, 'score_breakdown.red.foulPoints'),
				blue_auto_score = get_tag(i, 'score_breakdown.blue.autoPoints'),
				blue_teleop_score = get_tag(i, 'score_breakdown.blue.teleopPoints'),
				blue_adjust_points = get_tag(i, 'score_breakdown.blue.adjustPoints'),
				blue_total_score = get_tag(i, 'alliances.blue.score'),
				blue_foul_points = get_tag(i, 'score_breakdown.blue.foulPoints'),
				winner = strip_quotes(get_tag(i, 'winning_alliance'))
			where tba_match_key = v_match_key;
		end if;

		-- get the id for the match key, should always be there now
		select _id
		into v_match_id
		from `match`
		where tba_match_key = v_match_key;
        
        -- call insert_log(concat('got match_id: ', convert(v_match_id, CHAR)));
        
        call load_team_match(get_team(i, 'alliances.red.team_keys[0]'), v_match_id, 'red', 1);
        call load_team_match(get_team(i, 'alliances.red.team_keys[1]'), v_match_id, 'red', 2);
        call load_team_match(get_team(i, 'alliances.red.team_keys[2]'), v_match_id, 'red', 3);
        call load_team_match(get_team(i, 'alliances.blue.team_keys[0]'), v_match_id, 'blue', 1);
        call load_team_match(get_team(i, 'alliances.blue.team_keys[1]'), v_match_id, 'blue', 2);
        call load_team_match(get_team(i, 'alliances.blue.team_keys[2]'), v_match_id, 'blue', 3);
        
        set v_score_breakdown = get_tag(i, 'score_breakdown.red');
		call load_breakdown(v_match_id, 'red', v_score_breakdown);
        
        set v_score_breakdown = get_tag(i, 'score_breakdown.blue');        
		call load_breakdown(v_match_id, 'blue', v_score_breakdown);

		-- call insert_log('done with match');
        
		set i = i + 1;
	end while;
    
    call insert_log('Done!');
    
END$$
DELIMITER ;

