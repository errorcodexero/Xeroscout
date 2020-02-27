import requests
import mysql.connector as mysql
import datetime as dttm
import logging


def main():  
    logging.debug("main()")
    tba_event_key = '2020srrc'
    logging.info("TBA Event Key is " + tba_event_key)
    
    logging.debug("Calling TBA")
    url = 'https://thebluealliance.com/api/v3/event/' + tba_event_key + '/matches'
    url_parm = {"X-TBA-Auth-Key": "gOgFrY5ALa07kdXrXYKc1GIOTwkbom8OZYsPhFcpMg3fc5Te27RyG6Dq1sJEoFXT"}
    response = requests.get(url, params=url_parm)
    logging.info("Response text snippet: " + response.text[0:50])
    
    try:
        logging.info("Connect to Database")
        db = mysql.connect(host='localhost', user='root', passwd='root', 
                           db='scouting', port=3306)
        cursor = db.cursor()
        
        logging.info("Delete from staging")
        sql = "delete from staging"
        cursor.execute(sql)

        logging.info("Insert event match json into staging")
        sql = """
        insert into staging (data_type, json_data)
        values('json','%s')
        """ % response.text
        logging.debug(sql)
        cursor.execute(sql)

        logging.info("call load_matches()")
        sql = "call load_matches()"
        cursor.execute(sql)

    except Exception as e:
        db.rollback()
        logging.error(e)
        raise
    finally:    
        db.commit()
        cursor.close()
        db.close() 


if __name__ == "__main__":
    logging.basicConfig(filename = 'load_tba_event_match_2019.log',
                        level=logging.DEBUG)
    logging.info("Start " + str(dttm.datetime.now()))
    main()
    logging.info("End " + str(dttm.datetime.now()))
