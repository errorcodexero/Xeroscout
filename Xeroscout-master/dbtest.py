import mysql.connector

print("connecting to scouting on local")
conn = mysql.connector.connect(user='root', password='root',
                               host='127.0.0.1',
                               database='scouting')

cur = conn.cursor()
							   
query = "Select count(*) from team"

cur.execute(query)

data = cur.fetchall()

cur.close()
conn.close()
