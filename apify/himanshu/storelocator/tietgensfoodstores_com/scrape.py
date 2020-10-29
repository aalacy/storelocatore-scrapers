import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tietgensfoodstores_com')





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
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "https://tietgensfoodstores.com"
    locator_domain = "https://tietgensfoodstores.com"
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



    r = session.get('https://tietgensfoodstores.com/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    # logger.info(soup.prettify())

    for loc_data in soup.find_all('div',class_='location-data'):
        latitude = loc_data['data-lat']
        longitude = loc_data['data-lon']
        location_name = " ".join(loc_data.h3.text.strip().split()[1:])
        address= loc_data.find('div',class_='site-loc-address-wrapper')
        list_address = list(address.stripped_strings)
        street_address = list_address[0].strip()
        city = list_address[1].split(',')[0].strip()
        state = list_address[1].split(',')[1].split()[0].strip()
        zipp = list_address[1].split(',')[1].split()[-1].strip()
        phone_tag = loc_data.find('div',class_='site-loc-phone').text.strip()
        phone_list= re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
        if  phone_list !=[]:
            phone = phone_list[0].strip()
        else:
            phone = "<MISSING>"
        hours_of_operation = loc_data.find('div',class_='site-loc-hours').text.replace('Hours:','').strip()
        # logger.info(location_name,street_address,city,state,zipp,phone,hours_of_operation)


        # if store_number in addresses:
        #     continue

        # addresses.append(store_number)

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
