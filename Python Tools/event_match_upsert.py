import requests
import mysql.connector as mysql
import json
import numpy
import datetime as dttm


def main():
    
    log.write("\nBegin Script "+str(dttm.datetime.now())+" \n")
    
    db = mysql.connect(host=db_host, port=3306, user=db_user, passwd=db_passwd, db=db_name)
    cursor = db.cursor(buffered=True)
    
    # get the event id for the desired event we will be '2017orore'
    sql = '''
    select _id 
    from %s.`event`
    where tba_event_key = '%s'
    ''' % (db_name, tba_event_key)
    cursor.execute(sql)
    event_id = cursor.fetchone()
    event_id = event_id[0]
    print(event_id)
    log.write("event id is %i" % event_id)
    
    url = 'https://thebluealliance.com/api/v3/event/' + tba_event_key + '/matches'
    log.write("Calling "+url+"\n")
    url_parm = {"X-TBA-Auth-Key": tba_auth_key}
    response = requests.get(url, params=url_parm)
    log.write(str(response))
    j_matches = json.loads(response.text)
    log.write("\nNumber of matches to upsert %d \n"%(len(j_matches)))
    if len(j_matches) == 0:
        cursor.close()
        db.close()
        log.close()
        return
    try:
        for i in range(0, len(j_matches)):
            log.write("\nIteration %d \n" % i)
            print('iteration ' + str(i))
            match_number = j_matches[i]["match_number"]
            tba_match_key = j_matches[i]["key"]
            comp_level = j_matches[i]["comp_level"]
            set_number = j_matches[i]["set_number"]
            print ('match number ' + str(match_number))
            
            # get red and blue alliance team numbers out of json
            r_team_nbr = []
            b_team_nbr = []
            
            for k in range(0,3):
                log.write("Looking up team keys for k = %i\n" % k)
                log.write("Team key: %s \n" % j_matches[i]["alliances"]["red"]["team_keys"][k])
                r_team_nbr.insert(k, j_matches[i]["alliances"]["red"]["team_keys"][k])
                b_team_nbr.insert(k, j_matches[i]["alliances"]["blue"]["team_keys"][k])
                
            # check whether this match is already there
            log.write("Select for existing match\n")
            sql = '''
            select _id 
            from %s.`match` 
            where match_number = '%s' 
            and event_id = '%s'
            and comp_level = '%s'
            and set_number = '%s'
            ''' % (db_name, str(match_number), str(event_id), comp_level, str(set_number))
            print(sql)
            log.write("%s \n" % sql)
            cursor.execute(sql)
            if cursor.rowcount != 0:
                # write update later
                sql = 'update'
                print(sql)
                log.write(sql)
            else:
                # get scouting database team ids
                print('insert')
                log.write('insert')
                sql = '''
                select _id, team_number 
                from %s.team 
                where tba_team_key in('%s', '%s', '%s', '%s', '%s', '%s')
                ''' % (db_name, r_team_nbr[0], r_team_nbr[1], r_team_nbr[2], b_team_nbr[0], b_team_nbr[1],
                       b_team_nbr[2])
                print(sql)
                log.write("%s \n" % sql)
                cursor.execute(sql)
                team_mx = numpy.array(cursor.fetchall())
                r_team_id = []
                b_team_id = []
                
                for k in range(0,3):
                    print(k)
                    ref = numpy.where(team_mx == r_team_nbr[k])[0][0]
                    r_team_id.insert(k, team_mx[ref][0])
                    ref = numpy.where(team_mx == b_team_nbr[k])[0][0]
                    b_team_id.insert(k, team_mx[ref][0])
    
                # print(r1_team_id)
                # insert new records
                sql = '''
                insert into %s.`match` 
                    (event_id, tba_match_key, comp_level, set_number, match_number, red_1_team_id, red_2_team_id
                    , red_3_team_id, blue_1_team_id, blue_2_team_id, blue_3_team_id)
                values 
                    (%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
                ''' % (db_name, event_id, tba_match_key, comp_level, set_number, match_number,r_team_id[0], r_team_id[1],
                       r_team_id[2], b_team_id[0], b_team_id[1], b_team_id[2])
                print(sql)
                log.write("%s \n" % sql)
                cursor.execute(sql)
                # insert into team_match
    except Exception as e:
        db.commit()
        cursor.close()
        db.close()
        raise e
    # insert into team_match where no records yet exist
    db.commit()
    log.write("Insert into team_match\n")
    sql = '''
    insert into %s.team_match 
        (match_id, team_id, alliance, position) 
    (
        select _id, red_1_team_id, \"red\", 1 
        from %s.`match` m1 
        where not exists (select _id from team_match tm where m1._id = tm.match_id) 
    ) 
    union (
        select _id, red_2_team_id, \"red\", 2 
        from %s.`match` m2 
        where not exists (select _id from team_match tm where m2._id = tm.match_id) 
    ) 
    union (
        select _id, red_3_team_id, \"red\", 3 
        from %s.`match` m3 
        where not exists (select _id from team_match tm where m3._id = tm.match_id) 
    ) 
    union (
        select _id, blue_1_team_id, \"blue\", 1 
        from %s.`match` m4 
        where not exists (select _id from team_match tm where m4._id = tm.match_id) \
    )
    union (
        select _id, blue_2_team_id, \"blue\", 2  
        from %s.`match` m5
        where not exists (select _id from team_match tm where m5._id = tm.match_id) 
    ) 
    union (
        select _id, blue_3_team_id, \"blue\", 3  
        from %s.`match` m6 
        where not exists (select _id from team_match tm where m6._id = tm.match_id) 
    )
    ''' % (db_name, db_name, db_name, db_name, db_name, db_name, db_name)
    cursor.execute(sql)    
    db.commit()
    cursor.close()
    db.close()    
    log.write("Script Complete\n")
    log.close()  


if __name__ == "__main__":
    log = open("C:\logs\event_match_upsert_log.txt", 'a')
    db_host = 'localhost'
    db_user = 'root'
    db_passwd = 'root'
    db_name = 'scouting'
    tba_auth_key = 'gOgFrY5ALa07kdXrXYKc1GIOTwkbom8OZYsPhFcpMg3fc5Te27RyG6Dq1sJEoFXT'
    tba_event_key = '2020srrc'
    main()
