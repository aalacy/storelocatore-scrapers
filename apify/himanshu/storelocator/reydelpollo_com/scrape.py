import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('reydelpollo_com')





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
    locator_domain = "https://reydelpollo.com/"
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
    page_url = "https://reydelpollo.com/locations/"



    r= session.get('https://reydelpollo.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    for column in soup.find_all('div',class_='vc_row wpb_row vc_inner vc_row-fluid'):
        list_columns = list(column.stripped_strings)
        if len(list_columns) != 1:
            location_name = list_columns[0].strip()
            street_address = " ".join(list_columns[1].split(',')[:-2]).strip()
            city = list_columns[1].split(',')[-2].strip()
            state = list_columns[1].split(',')[-1].split()[0].strip()
            zipp = list_columns[1].split(',')[-1].split()[-1].strip()
            phone = list_columns[3].strip()
            hours_of_operation =  " ".join(list_columns).split('Hours:')[-1].strip().replace('–','-').strip()
            latitude = column.find('iframe')['src'].split('!1d')[-1].split('!3d')[0].split('!2d')[0].split('.')[0][-2:]+"."+column.find('iframe')['src'].split('!1d')[-1].split('!3d')[0].split('!2d')[0].split('.')[1]
            longitude = column.find('iframe')['src'].split('!1d')[-1].split('!3d')[0].split('!2d')[-1].strip()



            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')

            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            # logger.info("data===="+str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            return_main_object.append(store)


    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
