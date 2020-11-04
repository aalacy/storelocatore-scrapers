import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline= '') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addressess = []
    locator_domain = "https://unikwax.com"
    r = session.get("https://unikwax.com/studio-locations/?address%5B0%5D&tax%5Bregion%5D%5B0%5D&post%5B0%5D=location&distance=300&form=1&per_page=50&units=imperial&lat&lng", headers=headers)
    soup = bs(r.text,'lxml')
    for dt in json.loads(str(soup).split("var gmwMapObjects = ")[1].split("}}};")[0]+"}}}")['1']['locations']:
        adr = bs(dt['info_window_content'],"lxml")
        location_name = list(bs(dt['info_window_content'],"lxml").stripped_strings)[0]
        state = list(bs(dt['info_window_content'],"lxml").stripped_strings)[1].split(",")[-2].strip().split()[0]
        zipp = list(bs(dt['info_window_content'],"lxml").stripped_strings)[1].split(",")[-2].strip().split()[1]
        city = list(bs(dt['info_window_content'],"lxml").stripped_strings)[-3]
        street_address = " ".join(list(bs(dt['info_window_content'],"lxml").stripped_strings)[1].split(",")[:-3])
        page_url = (adr.find("a")['href'])
        latitude = dt['lat']
        longitude = dt['lng']
        hours_of_operation=''
        phone=''
        phone = bs(session.get(page_url, headers=headers).text,"lxml").find("a",{"class":"number"}).text.strip()
        try:
            hours_of_operation = " ".join(list(bs(session.get(page_url, headers=headers).text,"lxml").find("h5",text="Studio Hours").parent.stripped_strings)).replace("Studio Hours ",'')
        except:
            hours_of_operation ='<MISSING>'
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('US')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append( '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
    

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
