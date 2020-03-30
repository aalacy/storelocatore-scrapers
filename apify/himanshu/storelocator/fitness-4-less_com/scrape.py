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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://fitness-4-less.com/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main = soup.find('div',{"class":"e48-57"}).find('div',{"class":"x-tab-content"}).find_all('div',{"class":"x-tab-pane"})
    for location in main:
        geo=location.find('a')['href'].split('@')[1].split(',')
        loc_add=list(location.stripped_strings)
        del loc_add[1]
        del loc_add[1]
        del loc_add[2]
        del loc_add[2]
        store=[]
        st=loc_add[1].split(',')[3].strip().split(' ')
        store.append("https://fitness-4-less.com")
        store.append(loc_add[0])
        store.append(loc_add[1].split(',')[0].strip())
        store.append(loc_add[1].split(',')[2].strip())
        if len(st)==2:
            store.append(st[-2].strip())
            store.append(st[-1].strip())
        else:
            store.append(st[-1])
            store.append("<MISSING>")
        store.append('US')
        store.append(loc_add[1].split(',')[1])
        store.append(loc_add[2])
        store.append("Fitness 4 Less")
        store.append(geo[0].strip())
        store.append(geo[1].strip())
        del loc_add[0]
        del loc_add[0]
        del loc_add[0]
        del loc_add[0]
        store.append(' '.join(loc_add).replace('Follow our page','').strip())
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
