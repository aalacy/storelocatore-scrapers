import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dostoros_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

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
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.dostoros.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= session.get('https://www.dostoros.com/locations',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    a = soup.find('div',class_='locations').find('div',class_='columns').find_all('a')
    for i in a:
        # logger.info()
        r = session.get('https://www.dostoros.com'+i['href'],headers = headers)
        soup = BeautifulSoup(r.text,'lxml')
        info = soup.find('div',class_= 'locations').find('div',class_='columns').find('div',class_='list').find('div',class_='copy og')
        for loc in info.find_all('div',class_='place'):
            location_name = loc['data-name']
            address = loc.find('div',class_='info').find('div',class_='address')
            list_address = list(address.stripped_strings)
            street_address = list_address[1]
            csz = list_address[2].split(',')
            if len(csz) ==2:
                city = csz[0]
                state = csz[1].split()[0]
                zipp = csz[1].split()[-1]
            else:
                city = " ".join(csz[0].split()[:2])
                state = csz[0].split()[2]
                zipp = csz[0].split()[-1]
            hours = loc.find('div',class_='info').find('div',class_='hours')
            list_hours = list(hours.stripped_strings)
            if "hours" == list_hours[0] or "Now Open" == list_hours[0]:
                hours_of_operation = " ".join(list_hours[1:])
                # logger.info(hours_of_operation)
            else:
                hours_of_operation = "<MISSING>"
            coords = loc.find('div',class_='info').find('div',class_='mapit').a['href'].split('@')[-1].split('/')[0].split(',')
            if len(coords) >1:
                latitude = coords[0].strip()
                longitude =coords[1].strip()
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"




            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == None or x == "." else x for x in store]

            logger.info("data = " + str(store))
            logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
