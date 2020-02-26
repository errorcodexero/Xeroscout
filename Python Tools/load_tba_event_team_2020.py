import requests
import mysql.connector as mysql
import json
import datetime


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def get_events(cursor):
    f.write("Call API for events\n")
    url = "https://thebluealliance.com/api/v3/events/2020"
    url_parm = {"X-TBA-Auth-Key": tba_auth_key}
    response = requests.get(url, params=url_parm)
    j = json.loads(response.text)

    # From TBA...need to figure out how to import TBA
    # Objects for this sort of thing...
    event_type_names = {
        0: 'Regional',
        1: 'District',
        5: 'District Championship Division',
        2: 'District Championship',
        3: 'Championship Division',
        4: 'Championship Finals',
        6: 'Festival of Champions',
        99: 'Offseason',
        100: 'Preseason',
        -1: '--',
    }

    for i in range(0, len(j)):
        event_code = j[i]["event_code"]
        year = j[i]["year"]
        tba_event_key = j[i]["key"]
        name = j[i]["name"]
        short_name = j[i]["short_name"]
        event_type_code = j[i]["event_type"]
        event_type = event_type_names[event_type_code]
        event_district = "Not mapped"
        week = j[i]["week"] or -1
        location = j[i]["city"]

        print(event_code)
        print(year)
        print(tba_event_key)
        print(name)
        print(short_name)
        print(event_type_code)
        print(event_district)
        print(week)
        print(location)

        if event_district is None:
            if week is not None:
                sql_insert = '''
                INSERT INTO `scouting`.`event` 
                (tba_event_key, name, short_name, event_type, year ,week, location, tba_event_code) 
                VALUES (%s, %s, %s, %s, %d, %d, %s, %s)
                ''' \
                % ('\"' + tba_event_key + '\"', '\"' + name + '\"', '\"' + short_name + '\"',
                   '\"' + event_type + '\"', int(year), int(week), '\"' + location + '\"', '\"' + event_code + '\"')
            else:
                if short_name is not None:
                    sql_insert = '''
                    INSERT INTO `scouting`.`event`
                    (tba_event_key, name, short_name, event_type, year, location, tba_event_code) 
                    VALUES (%s, %s, %s, %s, %d, %s, %s)
                    '''\
                    % ('\"' + tba_event_key + '\"', '\"' + name + '\"', '\"' + short_name + '\"',
                       '\"'+ event_type + '\"', int(year), '\"' + location + '\"', '\"' + event_code + '\"')
                else:
                    sql_insert = '''
                    INSERT INTO `scouting`.`event` 
                    (tba_event_key, name, event_type, year, location, tba_event_code) 
                    VALUES (%s, %s, %s, %d, %s, %s)
                    '''\
                    % ('\"' + tba_event_key + '\"', '\"' + name + '\"', '\"' + event_type + '\"',
                       int(year), '\"' + location + '\"', '\"' + event_code + '\"')
        else:
            sql_insert = '''
            INSERT INTO `scouting`.`event` 
            (tba_event_key, name, short_name, event_type, event_district, year, week, location, tba_event_code)
            VALUES (%s, %s, %s, %s, %s, %d, %d, %s, %s)
            '''\
            % ('\"' + tba_event_key + '\"', '\"' + name + '\"', '\"' + short_name + '\"',
               '\"' + event_type + '\"', '\"' + event_district + '\"', int(year), int(week),
               '\"' + location + '\"', '\"' + event_code + '\"')
        # sql_insert = "INSERT INTO `scouting_steamworks`.`event` (tba_event_code, year)
        # VALUES (%s, %d)"%(event_code, int(year))
        print(sql_insert)
        cursor.execute(sql_insert)


def get_teams(cursor):
    for k in range(15, 17):
        url = 'https://thebluealliance.com/api/v3/teams/%d' % k
        url_parm = {"X-TBA-Auth-Key": tba_auth_key}
        response = requests.get(url, params=url_parm)
        txt = response.text

        f.write("TBA Called for k ="+str(k)+"\n")
        print('Requested https://thebluealliance.com/api/v3/teams/%d' % k)
        j = json.loads(txt)
        f.write("Loaded json " + str(k) + "\n")
        print("Before the inner for loop, team number is " + str(j[1]["team_number"]))
        
        for i in range (0, 500):
            # current_team_number = ((k * 500) + i ) if k != 0 else i
            print("Iteration " + str(k) + " " + str(i) + "\n")
            f.write("Iteration "+str(k) + " " + str(i) + "\n")
            
            try:
                print("Inside Try")
                print("i is "+str(i))
                print(j[i])
                team_number = j[i]["team_number"] or 0
                # print("Team "+str(team_number)+"\n")
                f.write("Getting Team "+str(team_number)+"\n")  
                team_name = j[i]["name"] or "None"
                team_name = team_name.replace('"', '')
                # print(team_name + "\n")
                team_key = j[i]["key"] or "None"
                # print (team_key + "\n")
                team_nickname = j[i]["nickname"] or "None"
                team_nickname = team_nickname.replace('"', '')
                # print (team_nickname  + "\n")
                team_region = "None"
                # print (team_region + "\n")
                team_locality = "None"
                # print (team_locality + "\n")
                team_country = j[i]["country"] or "None"
                # print (team_country + "\n")
                team_motto = j[i]["motto"] or "None"
                team_motto = team_motto.replace('"','')
                # print (team_motto + "\n")
                team_rookie_year = j[i]["rookie_year"] or 0
                # print (str(team_rookie_year) + "\n")

                print(team_name)
                
                if team_name is None:
                    f.write("Team name is empty.")
                    print ("Team name is empty.\n")
                    sql_insert = '''
                    INSERT INTO `scouting`.`team` 
                    (team_number, `name`, long_name, city, state_code, country, motto, rookie_year, tba_team_key) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %d, %s)
                    '''\
                    % ("\"" + str(team_number) + "\"", "\"" + team_nickname[0:255] + "\"",
                        ("\"" + team_name[0:255] + "\"" if is_ascii(team_name) else '"Foreign Names Not Supported"'),
                        "\"" + team_locality[0:255] + "\"", "\"" + team_region[0:40] + "\"", "\"" + team_country[0:255] + "\"", "\"" + team_motto[0:2000] + "\"", team_rookie_year,
                        "\"" + team_key + "\"")
                    # print(sql_insert)
                    
                else: 
                    f.write("Team name is not empty. Before  insert for team "+str(team_number)+"\n")
                    f.write("Construct insert for "+ team_name + "\n")
                    team_name = team_name[:255] #truncate team name to fit in database field
                    sql_insert = '''
                    INSERT INTO `scouting`.`team` 
                    (team_number, `name`, long_name, city, state_code, country, motto, rookie_year, tba_team_key) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %d, %s)
                    '''\
                    % ("\"" + str(team_number) + "\"", "\"" + team_nickname[0:255] + "\"",
                        ("\"" + team_name[0:255] + "\"" if is_ascii(team_name) else '"Foreign Names Not Supported"'),
                        "\"" + team_locality[0:255] + "\"", "\"" + team_region[0:40] + "\"",
                       "\"" + team_country[0:255] + "\"", "\"" + team_motto[0:2000] + "\"", team_rookie_year,
                        "\"" + team_key + "\"")
                    # print(sql_insert)

                f.write("Before  insert for team "+str(team_number)+"\n")
                print(("Before  insert for team "+str(team_number)+"\n"))
                # f.write(sql_insert+"\n")
                sql_insert = sql_insert.encode('utf-8','ignore')
                cur = cursor.execute(sql_insert)
                # print(cur)
                f.write("After insert for team "+str(team_number)+"\n")
                # print("After insert for team "+str(team_number)+"\n")
                
            except IndexError:
                print("Team with index %d does not exist on ttps://thebluealliance.com/api/v2/teams/%d" % (i, k))
                f.write("Team does not exists on "+str(k)+" "+str(i)+"\n")
                continue
            except KeyError:
                print("KeyError")
                f.write("KeyError\n")
            except mysql.IntegrityError:
                print("Team already exists")
                f.write("Team already exists\n")
                continue
            except Exception as e:
                print("Unhandled exception")
                print(str(e))
                raise e

def main():
    f.write("\nBegin Script " + str(datetime.datetime.now()) + "\n")
    try:
        f.write("Connect to database\n")
        db = mysql.connect(host=db_host, user=db_user, passwd=db_pw, db=db_name)
        cursor = db.cursor()

        f.write("Call Get Events\n")
        get_events(cursor)
        db.commit()

        # f.write("Call Get Teams\n")
        # get_teams(cursor)
        # db.commit()

        # clean up
        cursor.close()
        db.close()
    except mysql.Error as e:
        print("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
    except IndexError:
        print("Error")
    except:
        cursor.close()
        db.close()
        raise

    f.write("Script Complete\n")
    f.close()


if __name__ == "__main__":
    f = open("C:\logs\pylog.txt", 'a')
    db_host = 'localhost'
    db_user = 'root'
    db_pw = 'root'
    db_name = 'scouting_test'
    tba_auth_key = 'gOgFrY5ALa07kdXrXYKc1GIOTwkbom8OZYsPhFcpMg3fc5Te27RyG6Dq1sJEoFXT'
    main()
