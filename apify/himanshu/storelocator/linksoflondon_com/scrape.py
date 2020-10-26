import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('linksoflondon_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.linksoflondon.com/"
    r = session.get(base_url + 'eu-en/store-locator?sz=10000', headers=header)
    soup = BeautifulSoup(r.text, "lxml")



    for val in soup.find('div', {'id': 'store-location-results'}).find_all('div', {'class': 'store-information'}):
        # logger.info(val)

        store_number = val.find('a')['href'].split('=')[1].strip()


        locator_domain = base_url
        location_name =  val.find('a').text.strip()

        street_address =  val.find('div',{'class':'store-address'}).text.strip().split('\n')
        street_address123 = val.find('div', {'class': 'store-address'}).text.strip().replace('Address','').strip().replace('\x91','')
        street_address1 = re.sub('\s+',' ',street_address123)

        if len(street_address[-1].split(','))  == 2:
            city = street_address[-1].split(',')[0].strip()
            phone = soup.find('div',{'class':'store-phone'}).text.replace('Phone','').strip()
            state = soup.find('a',{'class':'google-map'})['href'].replace('%20','').split(',')[-1].strip()

        elif len(street_address[-1].split(','))  == 1:
            city = street_address[-1].split(' ')[0].strip()
            phone = soup.find('div',{'class':'store-phone'}).text.replace('Phone','').strip()
            state = '<MISSING>'

        zip = "<MISSING>"
        store_number = '<MISSING>'
        country_code = 'US'
        location_type = 'linksoflondon'
        latitude = '<MISSING>'
        longitude = '<MISSING>'

        if soup.find('div',{'class':'store-hours'}) != None:
            hours_of_operation  = soup.find('div',{'class':'store-hours'}).text.replace('Opening hours',' ').strip()

        store=[]
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address1 if street_address1 else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
