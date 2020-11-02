import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lionschoice_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    return_main_object = []

    base_url = "http://www.lionschoice.com"
    r = session.get("https://lionschoice.com/wp-admin/admin-ajax.php?action=store_search&lat=38.64466&lng=-90.33013&max_results=25&search_radius=10&autoload=1", headers=headers).json()
    # soup = BeautifulSoup(r.text, "lxml")

    for i in r:
        location_name=i['store'].replace('&#8217;',' ')
        address = i['address']
        city = i['city']
        state = i['state']
        zip= i['zip']
        hour_tmp =i['description']
        store_number =i['id']
        phone = i['phone'].replace('Not Available','<MISSING>')
        if  phone =='':
            phone= '<MISSING>'
        lat =i['lat']
        lng = i['lng']    
        hour1 = BeautifulSoup(hour_tmp, "lxml")
        hour = " ".join(list(hour1.stripped_strings)).replace('Order Online Delivery','')
        if hour =='':
            hour='<MISSING>'
        if 'Only Open for events' in hour:
            hour = '<MISSING>'
        # logger.info(location_name)
        store = []     
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(address if address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append('US')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hour if hour else '<MISSING>')
        store.append('<MISSING>')
    
   
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
