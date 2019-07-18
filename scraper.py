# import libraries
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import pandas as pd
import os
from pprint import pprint
from datetime import datetime as DateTime, timedelta as TimeDelta
from dotenv import load_dotenv
import csv
from io import StringIO
from sqlalchemy import create_engine

options = FirefoxOptions()
options.add_argument("--headless")
load_dotenv()
DBPATH = os.getenv('DBPATH')
s = '2019-09-15'
search_period = 30
trip_leght = 24
date = DateTime.strptime(s, "%Y-%m-%d")
data = []
db_table = 'flights'

def scrape(way):
    outbound_flights = driver.find_elements_by_css_selector("div[class^='flight-item ']")
    count_flights = len(outbound_flights)
    print('[', way ,'] Number of Flights:', count_flights)
    if count_flights == 0:
        pprint("Blocked: Sleeping a little")
        time.sleep(600)
        #outbound_flights = driver.find_elements_by_css_selector("div[class^='flight-item ']")
    for outbound_flight in outbound_flights:
        flighttimes=[]
        flightairports=[]
        flightdates=[]
        airline = outbound_flight.find_element_by_css_selector("span[class='airline-name']")
        duration = outbound_flight.find_element_by_css_selector("span[class^='flight-duration']")
        stops = outbound_flight.find_element_by_css_selector("span[class='flight-stops']")
        price = outbound_flight.find_element_by_css_selector("span[id^='tooltip-flight']")
        details = outbound_flight.find_elements_by_css_selector("div.col-xs-4.col-md-4:not(.no-padding)")
        for detail in details:
            flight_times = detail.find_element_by_css_selector("span[class='flight-time']")
            flighttimes.append(flight_times)
            flight_airports = detail.find_element_by_css_selector("span[class='flight-destination']")
            flightairports.append(flight_airports)
            flight_dates = detail.find_element_by_css_selector("span[class='flight-data']")
            flightdates.append(flight_dates)
        data.append({"way" : way, "airline" : airline.text , "departure_airport" : flightairports[0].text, "departure_date" : flightdates[0].text, "departure_time" : flightdates[0].text, "duration" : duration.text, "stops" : stops.text, "arrival_airport" : flightairports[1].text ,"arrival_date" : flightdates[0].text , "arrival_time" : flighttimes[1].text , "price" : price.text[3:-1]})

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
        pprint("INSERTED INTO DATABASE")

for day in range(search_period):
    outbound_date = (date + TimeDelta(days=day)).strftime('%Y-%m-%d')
    inbound_date = (date + TimeDelta(days=trip_leght) + TimeDelta(days=day)).strftime('%Y-%m-%d')
    print('To: ' + outbound_date + '  From: ' + inbound_date)
    # Loading webdriver and waiting for page
    urlpage = 'https://www.maxmilhas.com.br/busca-passagens-aereas/RT/HOU/RIO/' + outbound_date + '/' + inbound_date + '/1/0/0/EC'
    driver = webdriver.Firefox(options=options)
    driver.get(urlpage)
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(40)

    # Scraping elements from page
    try:
        scrape("Outbound")
        driver.find_element_by_xpath("//span[text()='volta']").click()
        scrape("Inbound")
    except: continue
    #Closing and Saving
    driver.quit()

df = pd.DataFrame(data)
engine = create_engine(DBPATH)
df.to_sql(db_table, engine, method=psql_insert_copy, if_exists='append', index=False)
