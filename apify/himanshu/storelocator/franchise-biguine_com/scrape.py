import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('franchise-biguine_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.franchise-biguine.com/trouver-mon-salon"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('div', {'class', 'pagination'}).findAll('li')[-2].findAll('span')[-1].get_text()
    for pages in range(1, int(exists)+1):
        data_url = "https://www.franchise-biguine.com/trouver-mon-salon/sort:distance/direction:asc/page:" + str(pages)
        logger.info(data_url)
        detail_url = session.get(data_url, headers=headers)
        detail_soup = BeautifulSoup(detail_url.text, "lxml")
        if detail_soup.find('div', {'class', 'appartment-listing'}):
            for values in detail_soup.find('div', {'class', 'appartment-listing'}).findAll('div', {'class', 'item'}):
                location_name = values.find('h2').get_text().strip()
                logger.info(location_name)
                address = re.sub(' +', ' ', values.find('p', {'class', 'street'}).get_text().strip().replace('\r\n', ' ').strip()).split(',')
                street_address = ' '.join(address[:-1])
                city = location_name
                state = "<MISSING>"
                if address[-2].split(' ')[-2].isdigit():
                    zip = address[-2].split(' ')[-2]
                elif address[-2].split(' ')[-3].isdigit():
                    zip = address[-2].split(' ')[-3]
                elif address[-2].split(' ')[-4].isdigit():
                    zip = address[-2].split(' ')[-4]
                elif address[-2].split(' ')[-5].isdigit():
                    zip = address[-2].split(' ')[-5]
                else:
                    zip = address[-2].split(' ')[-6]
                phone = address[-1].split(": ")[1]
                if values.find('p', {'class', 'lat'}):
                    latitude = values.find('p', {'class', 'lat'}).get_text().strip()
                else:
                    latitude = "<MISSING>"
                if values.find('p', {'class', 'lng'}):
                    longitude = values.find('p', {'class', 'lng'}).get_text().strip()
                else:
                    longitude = "<MISSING>"
                store = []
                store.append(base_url)                
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append("<MISSING>")
                store.append(data_url)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
