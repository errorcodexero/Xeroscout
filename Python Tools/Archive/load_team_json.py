import requests

#import pymysql as mysql

import json

#f = open("C:\logs\pylog.txt",'a')

team_json = open("./Output/team2018.json", 'a+')

tba_key = "gOgFrY5ALa07kdXrXYKc1GIOTwkbom8OZYsPhFcpMg3fc5Te27RyG6Dq1sJEoFXT"

i_max = 20

for k in range(0,i_max):
    print('Requested https://thebluealliance.com/api/v3/teams/%d'%(k))
    try:
        response = requests.get('https://thebluealliance.com/api/v3/teams/'+str(k)+'?X-TBA-Auth-Key='+tba_key)
    except:
        print('TBA team page limit reached at page ' + str(k))
        break
    txt = response.text
    #f.write("TBA Called for k ="+str(k)+"\n")

    team_json.write(txt)

    

team_json.close()
print('Script Complete')
