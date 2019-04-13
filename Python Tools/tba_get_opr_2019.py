"""
Script to load team stats like OPR from TBA for a given event
"""
import requests
import json
import mysql.connector as mysql
import datetime as dttm
import logging

print("Start")
# Connect to database
db = mysql.connect(host='localhost', port=3306, user='root', passwd='root', db='scouting')
cursor = db.cursor()

# Get team event stats from TBA
tba_event_key = '2019orwil'
url = 'https://thebluealliance.com/api/v3/event/' + tba_event_key + '/oprs'
url_parm = {"X-TBA-Auth-Key": "gOgFrY5ALa07kdXrXYKc1GIOTwkbom8OZYsPhFcpMg3fc5Te27RyG6Dq1sJEoFXT"}
response = requests.get(url, params=url_parm)

# Convert json
stats = json.loads(response.text)
oprs = stats["oprs"]
dprs = stats["dprs"]
ccwms = stats["ccwms"]

# print("Response text snippet: " + response.text[0:1000])

# Get the event_id
try:
    sql = "select _id from event where tba_event_key = '%s'" % tba_event_key
    cursor.execute(sql)
    event_id = cursor.fetchone()
except:
    cursor.close()
    db.close()
    raise

print("Event id: " + str(event_id))

for tba_team_key in oprs:
    print("OPR for " + tba_team_key + " is " + str(oprs[tba_team_key]) + ".")

    # Get the team_id
    try:
        sql = "select _id from team where tba_team_key = '%s'" % tba_team_key
        cursor.execute(sql)
        team_id = cursor.fetchone()
        if team_id is None:
            team_id = ["NULL",]
    except:
        cursor.close()
        db.close()
        raise

    # Get team_event_id
    try:
        sql = "select _id from team_event where team_id = %s and event_id = %s" % \
        (str(team_id[0]), str(event_id[0]))
        cursor.execute(sql)
        team_event_id = cursor.fetchone()
        if team_event_id is None:
            team_event_id = ["NULL",]
    except:
        cursor.close()
        db.close()
        raise

    # Insert or update opr in team_event
    try:
        sql = '''
        insert into team_event (_id, team_id, event_id, opr, dpr, ccwm)
        values (%s, %s, %s, %s, %s, %s)
        on duplicate key update
            opr = %s,
            dpr = %s,
            ccwm= %s
        ''' % (str(team_event_id[0]), str(team_id[0]), str(event_id[0]),
        str(oprs[tba_team_key]), str(dprs[tba_team_key]), str(ccwms[tba_team_key]),
        str(oprs[tba_team_key]), str(dprs[tba_team_key]), str(ccwms[tba_team_key]),)
        cursor.execute(sql)
        db.commit()
    except:
        cursor.close()
        db.close()
        raise
    # Check if row already

cursor.close()
db.close()