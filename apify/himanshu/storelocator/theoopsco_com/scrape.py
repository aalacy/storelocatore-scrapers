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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}

    r = session.get("https://theoopsco.com/pages/store-hours-by-location",headers=headers)
    soup = BeautifulSoup(r.text,'lxml')
    hoo = soup.find("div",{"class":"rte"})
    hff = str(hoo).split('width="491"/>')[1].split('<strong>')
    base_url = "https://www.theoopsco.com/"
    json_data = session.get("https://www.powr.io/cached/23423260.json", headers=headers).json()['content']['locations']

    for val in json_data:
       
        location_name = val['name']
        addr = val['address'].split(",")
        street_address = addr[0]
        city = addr[1].strip()
        state = addr[2].strip().split(" ")[0]
        zipp = addr[2].strip().split(" ")[1]
        phone = val['number']
        latitude = val['lat']
        longitude = val['lng']
        page_url = val['website']
        for i in hff:
            hour = i.replace("</strong>","").replace("<p>","").replace("</p>","").replace("</div>","").replace("\n"," ")
            if location_name in hour:
                hours_of_operation = hour.replace(location_name,"").replace('<p class="font_8">','').strip()

        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('US')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()


