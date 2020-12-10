import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    url_list= ["http://ilovetaste.com/app/taste_melrose/locations","http://ilovetaste.com/app/taste_palisades/locations"]

    for url in url_list:

        soup = BeautifulSoup(session.get(url).text,"lxml")
        
        info = list(soup.find("div",{"class":"side-widget below"}).stripped_strings)

        location_name = soup.find("div",{"id":"logo"}).find("img")['alt']
        street_address = info[0].split(',')[0]
        city = info[0].split(',')[1]
        state = info[0].split(',')[2].split( )[0]
        zipp = info[0].split(',')[2].split( )[1]
        phone  = info[-1].replace("Phone: ","")

        hours = " ".join(list(soup.find_all("div",{"class":"side-widget below"})[1].stripped_strings))
        page_url = url

        store = []
        store.append("http://ilovetaste.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Restaurant")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        
        yield store

      
        
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

