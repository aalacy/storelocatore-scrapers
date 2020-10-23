import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mrchow_com')





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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # logger.info("soup ===  first")

    base_url = "https://mrchow.com"
    r = session.get("https://mrchow.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "mrchow"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for script_link in soup.find_all('div', {'class': 'dropdownMenuInner'}):
        for script_contact_link in script_link.find_all('a'):
            # list_link = list(script_link.stripped_strings)
            if 'contact' in script_contact_link['href']:
                location_url = base_url + script_contact_link['href']
                # logger.info("link ==== " + str(location_url))
                r_location = session.get(location_url, headers=headers)
                soup_location = BeautifulSoup(r_location.text, "lxml")
                list_address = list(soup_location.find('div', {'id': 'restaurantContact'}).stripped_strings)
                # logger.info("data ==== " + str(list_address))
                tel_index = [i for i, s in enumerate(list_address) if 'Tel:' in s]
                fax_index = [i for i, s in enumerate(list_address) if 'Fax:' in s]

                phone = list_address[tel_index[0]].split(':')[-1].strip()
                hours_of_operation = ', '.join(list_address[1:tel_index[0]])
                location_name = list_address[0]

                if len(fax_index) > 0:
                    full_address = list_address[fax_index[0]+1:]
                else:
                    full_address = list_address[tel_index[0]+1:]

                full_address = ','.join(full_address)

                if len(full_address.split(',')[-1].strip().split(' ')) > 1:
                    street_address = ','.join(full_address.split(',')[:-2])
                    city = full_address.split(',')[-2]
                    if len(street_address) == 0:
                        street_address = full_address.split(',')[0]
                        city = '<MISSING>'

                    state = full_address.split(',')[-1].strip().split(' ')[0]
                    zipp = full_address.split(',')[-1].strip().split(' ')[1][-6:]
                else:
                    street_address = ','.join(full_address.split(',')[:-3])
                    city = full_address.split(',')[-3]
                    if str(full_address.split(',')[-1])[-5:].isdigit():
                        zipp = full_address.split(',')[-1][-5:]
                        state = full_address.split(',')[-2]
                    else:
                        zipp = full_address.split(',')[-2][-5:]
                        state = full_address.split(',')[-1]

                if not zipp.isdigit():
                    continue

                # logger.info('full_address ==== ' + str(full_address))
                # logger.info('street_address ==== ' + str(street_address))
                # logger.info('city ==== ' + str(city))
                # logger.info('zipp ==== ' + str(zipp))
                # logger.info('state ==== ' + str(state))

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
