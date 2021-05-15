#!/usr/bin/env python3
# import libraries
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
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

load_dotenv()
DBPATH = os.getenv('DBPATH')

s = '2021-07-01'
search_period = 1
trip_leght = 180
departure_city = 'BSB'
arrival_city = 'IAH'
data = []
db_table = 'flights'

def create_run(engine):
    q = engine.execute("INSERT INTO runs(departure_city,arrival_city,datetime) VALUES ('" + departure_city + "', '" + arrival_city + "', current_timestamp) RETURNING id;")
    q_result = q.first()[0]
    return q_result

def run_driver(run_number):
    def scrape(way):
        outbound_flights = driver.find_elements_by_css_selector("div[class^='css-19ivl5o']")
        count_flights = len(outbound_flights)
        print('Number of Flights:', count_flights)
        if count_flights == 0:
            pprint("Blocked: Sleeping a little")
            time.sleep(600)
        for outbound_flight in outbound_flights:
            airline = outbound_flight.find_element_by_css_selector("div[class='css-1gaumbn']")
            duration = outbound_flight.find_element_by_css_selector("span[class='time']")
            stops = outbound_flight.find_element_by_css_selector("span[class='stops']")
            price = outbound_flight.find_element_by_css_selector("h5[class='highlight-price']")
            price = price.text[3:-1].replace('.','')
            price = price.replace(',','.')
            origin_details = outbound_flight.find_element_by_css_selector("div[class='css-1ka7a5g']")
            destination_details = outbound_flight.find_element_by_css_selector("div[class='css-m0x1fd']")
            destination_airport = destination_details.text[:-6]
            destination_time = destination_details.text[4:]

            if "\n" in destination_airport:
                destination_airport = destination_airport[:-3]
            if "\n+1" in destination_time:
                destination_time = destination_time[:-3]
                o_date = DateTime.strptime(outbound_date, "%Y-%m-%d")
                arrival_date = (o_date + TimeDelta(days=1)).strftime('%d/%m/%Y')
            else:
                arrival_date = DateTime.strptime(outbound_date, "%Y-%m-%d")
                arrival_date = arrival_date.strftime('%d/%m/%Y')
            pprint(arrival_date)
            #data.append({"way" : way, "airline" : airline.text[4:] , "departure_airport" : origin_details.text[:-6], "departure_date" : outbound_date, "departure_time" : origin_details.text[4:], "duration" : duration.text, "stops" : stops.text, "arrival_airport" : destination_airport,"arrival_date" : arrival_date , "arrival_time" : destination_time , "price" : price , "run_id" : run_number})
        #pprint(data)
    for day in range(search_period):
        date = DateTime.strptime(s, "%Y-%m-%d")
        outbound_date = (date + TimeDelta(days=day)).strftime('%Y-%m-%d')
        #inbound_date = (date + TimeDelta(days=trip_leght) + TimeDelta(days=day)).strftime('%Y-%m-%d')
        urlpage = 'https://www.maxmilhas.com.br/busca-passagens-aereas/OW/' + departure_city + '/' + arrival_city + '/' + outbound_date + '/1/0/0/EC'
        options = FirefoxOptions()
        #options.add_argument("--headless")
        driver = webdriver.Firefox(options=options,executable_path=r'/usr/local/bin/geckodriver')
        driver.get(urlpage)
        print('IDA: ' + outbound_date)
        time.sleep(10)
        #for _ in range(60):
        #    html = driver.find_element_by_tag_name('html')
        #    html.send_keys(Keys.PAGE_DOWN)
        #    time.sleep(0.5)
        scrape("Outbound")

        driver.quit()

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
#    run_number = create_run(engine)
    run_number = 0
    run_driver(run_number)
#    insert_db(data,engine)
    pprint("Finished")

if __name__ == "__main__":
    main()
