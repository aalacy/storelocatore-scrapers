import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thebeerstore_ca')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    base_url = "https://www.thebeerstore.ca/stores/"
    # it will used in store data.
    locator_domain = "https://www.thebeerstore.ca/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    addresses = []
    exists = soup.findAll('div', {'class', 'city_list'})
    if exists:
        for data in soup.findAll('a', {'class', 'site_default_btn'}):
            data_url = data.get('href')
            page_url = data_url
            city = data.parent.findAll('li')[-1].get_text().split(',')[0].replace('\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t', '').strip()
            # logger.info(city)
            detail_url = session.get(data_url, headers=headers)
            detail_soup = BeautifulSoup(detail_url.text, "lxml")
            detail_data = detail_soup.find('div', {'class', 'store_detail'})
            if detail_data:

                location_name = detail_data.find('h2').get_text().strip()

                store_number = detail_data.find('h2').find_next('p').get_text().split('#')[1].strip()
                address = detail_data.find('h4').find_next('p').get_text().replace('\n', '').split(',')
                phone = detail_data.find('div', {'class': 'pnum'}).find('p').get_text().strip().replace("\n", '')
               
                try:
                    hours = detail_data.find('div',class_='rite_col')
                    list_hours = list(hours.stripped_strings)


                    list_hours = [el.replace('\n\t\t\t\t\t\t\t\t\t\t',' ') for el in list_hours]

                    if  "—" != list_hours[2]:
                        hours_of_operation = " ".join(list_hours[1:]).strip()
                    # ['Store Hours', 'Mon', '—', 'Tues', '—', 'Wed', '—', 'Thurs', '—', 'Fri', '—', 'Sat', '—', 'Sun', '—']

                    else:
                        hours_of_operation = "<MISSING>"
                except:
                    hours_of_operation = "<MISSING>"

                street_address = address[0].strip()
                zipp = address[1].strip()
                state = "<MISSING>"
                latitude = detail_soup.find('div', {'class': 'store_map'}).find('img').get('src').split('|')[-1].split('&')[0].split(',')[0]
                longitude = detail_soup.find('div', {'class': 'store_map'}).find('img').get('src').split('|')[-1].split('&')[0].split(',')[1]

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == "" or x == None else x for x in store]
                if store_number in addresses:
                    continue
                addresses.append(store_number)


                # logger.info("data = " + str(store))
                # logger.info(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)

            else:
                pass
        return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
