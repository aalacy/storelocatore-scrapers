import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('webeca_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.webeca.com/"
    loacation_url = 'https://www.webeca.com/our-eye-doctors/'
    addresses= []
    r = session.get(loacation_url, headers=header)
    soup = BeautifulSoup(r.text, "html.parser")

    vk = soup.find_all('td', {'valign': 'top'})
    for x in vk:
        for z in x.find_all('a'):
            r = session.get(z['href'], headers=header)
            soup = BeautifulSoup(r.text, "html.parser")
            if soup.find('address') != None:
                locator_domain =base_url
                location_name = ''
                if soup.find('h1',{'class':'location-name'}) != None:
                    location_name = soup.find('h1',{'class':'location-name'}).text.strip()
                street_address = soup.find('address').text.strip().split(',')[0].split('  ')[0]
                city = soup.find('address').text.strip().split(',')[0].split('  ')[-1].strip()
                state = soup.find('address').text.strip().split(',')[1].strip().split(' ')[0]
                zip = soup.find('address').text.strip().split(',')[1].strip().split(' ')[1]
                country_code = "US"
                store_number = ''
                phone = soup.find('div',{'class':'phone-number'}).text.strip()
                location_type = 'webeca'
                latitude = ''
                longitude = ''
                hours_of_operation = ' '.join(soup.find('div',{'class':'hours'}).find('div',{'class':'times'}).text.strip().split('\n'))
                page_url = z['href']

                if street_address in addresses:
                    continue
                addresses.append(street_address)

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')

                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')

                logger.info("data=====",str(store))
                # return_main_object.append(store)
                yield store

    # return return_main_object

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
