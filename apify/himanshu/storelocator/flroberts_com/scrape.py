import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('flroberts_com')




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
    base_url = "https://www.flroberts.com/locations/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main = soup.find('section').find('div',{"class":"col-sm-12 default-area"})
    for data in main.find('div',{"id":'convenience-stores'}).find_all('div',{"class":"col-sm-6"}):
        val=data.find('a')['id'].replace('click-info','')
        geo=list(main.text.split("var "+val)[1].split('(')[1].split(')')[0].split(', '))
        location=list(data.stripped_strings)
        store=[]
        logger.info(location)
        store.append("https://www.flroberts.com")
        store.append(location[0])
        del location[0]
        store.append(location[0])
        del location[0]
        store.append(location[0].split(',')[0].strip())
        store.append(location[0].split(',')[1].strip())
        del location[0]
        store.append("<MISSING>")
        store.append('US')
        store.append("<MISSING>")
        store.append(location[0])
        del location[0]
        store.append("flroberts")
        store.append(geo[0])
        store.append(geo[1])
        del location[0]
        store.append(''.join(location))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
