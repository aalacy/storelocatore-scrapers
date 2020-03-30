import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import unicodedata

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Connection': 'keep-alive',
    }
    base_url = "https://rosebudrestaurants.com/"
    location_url1 = "https://rosebudrestaurants.com/"
    r = session.get(location_url1, headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    a = soup.find("ul",{"class":"0 sub-menu raven-submenu"})
    k = (a.find_all("a"))
    for i in k :
        location_name = (i.text)
        link = (i['href'])
        r1 = session.get(link, headers=headers)
        soup1= BeautifulSoup(r1.text,"lxml")
        a1 = soup1.find("div",{"class":"elementor-text-editor elementor-clearfix"})
        state = (a1.text.split("PHONE")[0].split(" ")[-1])
        city = (a1.text.split("PHONE")[0].split(" ")[-2])
        street_address = " ".join(a1.text.split("PHONE")[0].split(" ")[:-2]).replace("ADDRESS","")

        phone = (a1.text.split("PHONE")[1].split("LUNCH")[0].split("BRUNCH")[0])
        mp = "".join(a1.text.split("PHONE")[1].split("-")[2:])
        hours_of_operation = (mp.replace('6444','').replace('1900','').replace('1000','').replace('1117','').replace('0900','').replace('9800','').replace('6000','').replace('7676','').replace('1111',"").replace("pm","pm "))
        store = []
        store.append("https://rosebudrestaurants.com/")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>" )
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(link)
        for i in range(len(store)):
            if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize(
                        'NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–", "-") if type(x) ==
                     str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
