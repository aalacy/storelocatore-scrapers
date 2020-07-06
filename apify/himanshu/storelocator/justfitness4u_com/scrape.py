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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://www.justfitness4u.com/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        }

    location_url = "https://justfitness4u.com/contact/"

    r = session.get(location_url, headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    
    loc = soup.find_all(["div","h4"],{"class":"elementor-heading-title elementor-size-default"})
    add = soup.find_all("iframe",{"class":"lazyload"})
    phone_t = soup.find_all("p",{"class":"elementor-icon-box-description"})

    for j,i,k in zip(add,loc,phone_t):
        phone = k.text
        location_name = j["aria-label"]
        raw = i.text
        sp = raw.split(",")
        street_address = sp[0].strip()
        city = sp[1].strip()
        sp2 = sp[-1].split(" ")
        state = sp2[-2]
        zipp = sp2[-1]
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Gym")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(location_url)
        yield store
    

    

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
