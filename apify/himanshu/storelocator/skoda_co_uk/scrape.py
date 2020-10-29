import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('skoda_co_uk')


session = SgRequests() 
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    address = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://www.skoda.co.uk/"
    
    json_data = session.get("https://retailers.skoda-auto.com/api/210/en-gb/Dealers/GetDealers?SearchType=0&ClientDate=2020-06-03%2015:20:49",headers=headers).json()['Items']

    for data in json_data:
        
        location_name  = data['Name']
        
        street_address = data['Address']['Street']
        city = data['Address']['City']
        state = data['Address']['District']
        zipp = data['Address']['ZIP']
        lat = data['Address']['Latitude']
        lng = data['Address']['Longitude']
        store_number = data['GlobalId'].split("-")[-1]
        # logger.info(store_number)
        day = {"1":"Monday","2":"Tuesday","3":"wednesday","4":"Thurday","5":"Friday","6":"Saturday","7":"Sunday"}
        location_data = session.get("https://retailers.skoda-auto.com/api/210/en-gb/Dealers/GetDealer?id="+str(data['GlobalId'])+"&clientDate=2020-06-05%2014:58:20").json()

        phone = location_data['Contact']['Telephone']

        page_url = location_data['Contact']['WebUrl']
        hours = ''
        if location_data['Sale']['Items']:
            for hr in location_data['Sale']['Items'][0]['OpeningHours']:
                if "Interval1To" in hr:
                    hours+= day[str(hr['WeekDay'])]+" " + datetime.strptime(hr['Interval1From'],"%H:%M:%S").strftime("%I:%M %p")+" - "+datetime.strptime(hr['Interval1To'],"%H:%M:%S").strftime("%I:%M %p")+" "
                else:
                    hours+= day[str(hr['WeekDay'])]+" Closed "
        else:
            hours = "<MISSING>"
        

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("UK")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()




