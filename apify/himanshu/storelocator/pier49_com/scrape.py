import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pier49_com')





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



    base_url = "https://pier49.com"
    r = session.get("https://pier49.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url=""

    for script in soup.find_all('div', {'class': re.compile('row_inner col_align_middle gutter-none')}):
        # coords = soup.find(lambda tag: (tag.name == "a" and "Google Maps" in tag.text))
        # logger.info(coords)
        list_store_data = list(script.stripped_strings)
        # logger.info(str(len(list_store_data))+' == list_store_data === '+str(list_store_data))
        if len(list_store_data) > 0 :
            if 'ORDER ONLINE' in list_store_data:
                list_store_data.remove('ORDER ONLINE')

            if 'ORDER ONLINE' in list_store_data:
                list_store_data.remove('ORDER ONLINE')

            if '-Delivery Only-' in list_store_data:
                list_store_data.remove('-Delivery Only-')

            if 'Hours' in list_store_data:
                list_store_data.remove('Hours')

            if 'Facebook' in list_store_data:
                list_store_data.remove('Facebook')

            if 'Google Maps' in list_store_data:
                list_store_data.remove('Google Maps')

            # logger.info(str(len(list_store_data)) + " = script ------- " + str(list_store_data))

            location_name = list_store_data[0]
            phone = list_store_data[1]

            try:
                street_address = list_store_data[2]
                city = list_store_data[3].split(',')[0]
                zipp = list_store_data[3].split(',')[1].strip().split(' ')[-1]
                state = list_store_data[3].split(',')[1].strip().split(' ')[-2]
                hours_of_operation= ",".join(list_store_data[4:]).replace('ORDER ONLINE (NEW!)','').strip()
                # logger.info(hours_of_operation)

            except:
                street_address = '<MISSING>'
                city = '<MISSING>'
                zipp = '<MISSING>'
                state = '<MISSING>'
                hours_of_operation = ",".join(list_store_data[2:])
                # logger.info(hours_of_operation)

            country_code = 'US'
            store_number = '<MISSING>'
            latitude = '<MISSING>'
            longitude = '<MISSING>'

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == None or x == '' else x for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            if street_address != '<MISSING>':
                return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
