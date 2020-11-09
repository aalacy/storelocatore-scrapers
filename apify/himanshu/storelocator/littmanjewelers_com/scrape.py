import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import html5lib
from sgrequests import SgRequests
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('littmanjewelers_com')
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }
    session = SgRequests()
    base_url = "https://www.littmanjewelers.com/"  
    r = session.get("https://www.littmanjewelers.com/Service/storelocatorhandler.ashx?action=FindStores&location=89025&radius=1000000&fromPg=other", headers=headers).json()
    for h in r:
        hours_of_operation = 'Monday: ' +  str(h['StoreHours']['MondayOpen']) + ' - ' + str(h['StoreHours']['MondayClose']) + ' Tuesday: ' +  str(h['StoreHours']['TuesdayOpen']) + ' - ' +  str(h['StoreHours']['TuesdayOpen']) + ' Wednesday ' +  str(h['StoreHours']['WednesdayOpen']) + ' - ' +   str(h['StoreHours']['WednesdayClose']) + ' Thursday ' +  str(h['StoreHours']['ThursdayOpen']) + ' - ' +  str(h['StoreHours']['ThursdayClose']) + ' Friday ' +  str(h['StoreHours']['FridayOpen']) + ' - ' +  str(h['StoreHours']['FridayClose']) + ' Saturday ' +  str(h['StoreHours']['SaturdayOpen']) + ' - ' +  str(h['StoreHours']['SaturdayClose']) + ' Sunday ' +  str(h['StoreHours']['SundayOpen']) + ' - ' +  str(h['StoreHours']['SundayClose'])
        store = []
        store.append("https://www.littmanjewelers.com/")
        store.append(h['StoreName'])
        store.append(h['AddressLine1'])
        store.append(h['City'])
        store.append(h['State'])
        store.append(h['ZipCode'])   
        store.append("US")
        store.append(h['StoreNumber'])
        store.append(h['Phone'])
        store.append(h['StoreName'])
        store.append(h['Latitude'])
        store.append(h['Longitude'] )
        store.append(hours_of_operation.replace("Tuesday: 10:00 - 10:00","Tuesday: 10:00 - 22:00").replace("Tuesday: 09:00 - 09:00","Tuesday: 09:00 - 21:00").replace("Tuesday: 12:00 - 12:00","Tuesday: 12:00 - 00:00"))
        store.append("<MISSING>")
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
