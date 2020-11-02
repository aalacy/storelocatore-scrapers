import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import requests
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bluebottlecoffee_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    payload = {}
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    }

    r = session.get("https://bluebottlecoffee.com/api/cafe_search/fetch.json?cafe_type=all&coordinates=false&query=true&search_value=all",headers=headers).json()

    for q in r['cafes']:
        for dt in r['cafes'][q]:
            latitude = dt['latitude']
            longitude = dt['longitude']
            name = dt['name']
            address = bs(dt['address'],'lxml')
            full = list(address.stripped_strings)
            if "00000" in full:
                continue 
            if full[-1]=="Ttukseom station — exit #1":
                del full[-1]
            city = full[-1].split(",")[0]
            zipp =full[-1].split(",")[-1].split( )[-1]
            states = " ".join(full[-1].split(",")[-1].split( )[:-1])
            if len(states)==2:
                addressses =" ".join(full[:-1])
                page_url = dt['url']
                r1 = session.get(page_url)
                soup = bs(r1.text,'lxml')
                hours =''
                hours_of_operation=''
                for h in  soup.find("div",{"class":"mw5 mw-100-ns"}).find_all(("div",{"class":"dt wi-100 pb10 f5"})):
                    hours = hours + ' '+" ".join(list(h.stripped_strings))
                hours_of_operation =  hours.split("We’ve reopened")[0].split("To help slow the")[0]
                hours_of_operation= re.sub(r"\s+", " ",hours_of_operation)
                # logger.info(hours_of_operation)
                store = []
                store.append("https://bluebottlecoffee.com/")
                store.append(name)
                store.append(addressses)
                store.append(city)
                store.append(states)
                store.append(zipp)
                store.append("US")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
                store.append(page_url)
                # logger.info(store)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
        

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
