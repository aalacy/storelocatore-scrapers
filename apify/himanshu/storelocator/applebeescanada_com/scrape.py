import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('applebeescanada_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.applebeescanada.com/restaurants/location-finder"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'location'})
    for data in exists.findAll('a'):
        if data.get('href') == '' or data.get('href') is None:
            state = data.get_text().strip()
            # logger.info(state)
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        else:
            data_url = "http://www.applebeescanada.com" + data.get('href')
            page_url = data_url
            detail_url = session.get(data_url, headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            detail_block = detail_soup.find('div', {'class', 'blocks'})
            if detail_block:
                location_name = detail_soup.find('h1').get_text().strip()
                address = detail_block.find('h5').get_text().strip().split(',')
                street_address = ''.join(
                    address[:-1]).strip().replace('Calgary', '').replace('Alberta', '').strip()
                # logger.info(street_address)
                if address[0][0:2].isdigit():
                    city = address[-2]
                elif "Sunridge Mall" in address[0]:
                    city = address[-3]
                else:
                    city = address[0]
                ca_zip_list = re.findall(
                    r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(address[-1]))
                if ca_zip_list != []:
                    zip = ca_zip_list[0].strip()
                else:

                    zip = "<MISSING>"
                phone = detail_block.find('h5').find_next(
                    'h3').get_text().strip()[5:]
                if "Meet" in detail_block.find('h5').find_next('p').find_next('p').get_text().strip():
                    hours_of_operation = detail_block.find('h5').find_next('p').get_text().strip().replace(
                        'Winter Hours', '').replace(', Name: Peter Ennis', '').replace("&", 'to').strip()

                else:
                    hours = detail_block.find('h5').find_next('p').get_text().strip(
                    ) + ", " + detail_block.find('h5').find_next('p').find_next('p').get_text().strip()
                    if "Heather Lennie" in hours:
                        hours_of_operation = "<MISSING>"
                    else:
                        hours_of_operation = hours.replace(
                            ', Name: Peter Ennis', '').replace('&', 'to').strip()
                # logger.info(hours_of_operation)
                store = []
                store.append("http://www.applebeescanada.com")

                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("CA")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hours_of_operation.encode(
                    'ascii', 'ignore').decode('ascii').strip())
                store.append(page_url)
                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]
                # logger.info(store[-2])
                # logger.info("data == " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                return_main_object.append(store)
            else:
                pass
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
