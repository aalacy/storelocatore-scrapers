import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thesaddleranch_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    logger.info("soup ===  first")

    base_url = "http://www.thesaddleranch.com"
    r = session.get("http://www.thesaddleranch.com/locations", headers=headers)
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
    location_type = "thesaddleranch"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    for script in soup.find('div', {'class': 'entry-content'}).find_all('a'):
        r_location = session.get(script['href'], headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        logger.info("script  ==== "+str(list(soup_location.find('address').stripped_strings)))
        list_address = list(soup_location.find('address').stripped_strings)
        location_name = list_address[0]
        street_address = list_address[1]
        city = list_address[2].strip().split(',')[0]
        state = list_address[2].strip().split(',')[1].strip().split(' ')[0]
        zipp = list_address[2].strip().split(',')[1].strip().split(' ')[1]
        phone = list_address[-1]
        country_code = 'US'
        hours_of_operation = ','.join(list(soup_location.find('div',{'class':"location-hours"}).stripped_strings))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
