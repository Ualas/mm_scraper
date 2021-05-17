import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import os
from pprint import pprint
from datetime import datetime as DateTime, timedelta as TimeDelta
from dotenv import load_dotenv
import csv
from io import StringIO
from sqlalchemy import create_engine
import undetected_chromedriver as uc

load_dotenv()
DBPATH = os.getenv('DBPATH')

routes = [
            # {"startdate" : '2021-07-01', "departure_city" : 'RIO', "arrival_city" : 'CUN'},
            {"startdate" : '2021-07-01', "departure_city" : 'RIO', "arrival_city" : 'MEX'},
            {"startdate" : '2021-07-01', "departure_city" : 'RIO', "arrival_city" : 'AUA'}
            ]

search_period = 30
data = []
day_data = []
flights_data = []
db_table = 'flights'

def create_run(engine, departure_city, arrival_city):
    run_route = departure_city + " to " + arrival_city
    q = engine.execute("INSERT INTO runs(departure_city,arrival_city,datetime, route) VALUES ('" + departure_city + "', '" + arrival_city + "', current_timestamp, '"+run_route+"') RETURNING id;")
    q_result = q.first()[0]
    return q_result

def run_driver(run_number, s, departure_city, arrival_city):
    def scrape(way):
        outbound_flights = driver.find_elements_by_css_selector("div[class^='css-lhlz7a']")
        count_flights = len(outbound_flights)
        print('Number of Flights:', count_flights)
        if count_flights == 0:
            pprint("Blocked: Sleeping a little")
            time.sleep(600)
        for outbound_flight in outbound_flights:
            price = outbound_flight.find_element_by_css_selector("h5[class='highlight-price']")
            price = price.text[3:].replace('.','').replace(',','.')
            if price:
                flights_data.append({"departure_date" : outbound_date, "price" : price, "run_id" : run_number})

    for day in range(search_period):
        date = DateTime.strptime(s, "%Y-%m-%d")
        outbound_date = (date + TimeDelta(days=day)).strftime('%Y-%m-%d')
        urlpage = 'https://www.maxmilhas.com.br/busca-passagens-aereas/OW/' + departure_city + '/' + arrival_city + '/' + outbound_date + '/1/0/0/EC'
        options = uc.ChromeOptions()
        #options.add_argument("--headless")
        driver = uc.Chrome(options=options)
        driver.get(urlpage)
        #driver.minimize_window()
        print(departure_city, 'to', arrival_city, 'em ' + outbound_date)
        time.sleep(40)
        scrape("Outbound")
        driver.quit()
    
    return flights_data

def insert_db(data,engine):
    def psql_insert_copy(table, conn, keys, data_iter):
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)
            columns = ', '.join('"{}"'.format(k) for k in keys)
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name
            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)

    df = pd.DataFrame(data)
    df.to_sql(db_table, engine, method=psql_insert_copy, if_exists='append', index=False)

def main():
    engine = create_engine(DBPATH)
    for route in routes:
        startdate = route['startdate']
        departure_city = route['departure_city']
        arrival_city = route['arrival_city']
        
        run_number = create_run(engine, departure_city, arrival_city)
        data = run_driver(run_number, startdate, departure_city, arrival_city)
        insert_db(data, engine)

    print("Finished")

if __name__ == "__main__":
    main()
