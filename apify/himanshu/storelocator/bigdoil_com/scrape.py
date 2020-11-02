import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bigdoil_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():

    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',

    }

    # it will used in store data.
    locator_domain = "http://www.bigdoil.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "bigdoil"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get('http://www.bigdoil.com/locations/', headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    val = soup.find('section', class_="entry")
    for result in val.find_all('div', class_='vc_col-sm-4'):
        # logger.info(result)
        for p in result.find_all('p'):
            for br in p.find_all('br'):
                br.replace_with('|')
            p0 = str(p).split('|')
            for p1 in p0:
                if "</a>" not in str(p1):
                    list_p1 = p1.split('\n')[-1].split('–')
                    if len(list_p1) == 2:
                        # logger.info(list_p1)
                        street_address = "".join(
                            list_p1[-1].split(',')[0].encode('ascii', 'ignore').decode('ascii').strip())
                        city = "".join(
                            list_p1[-1].split(',')[-1].split()[0].encode('ascii', 'ignore').decode('ascii').strip())
                        state = "".join(
                            list_p1[-1].split(',')[-1].split()[-1].replace('</p>', "").encode('ascii', 'ignore').decode('ascii').strip())
                        location_name = "".join(
                            list_p1[0].replace('<p>', "").strip()) + " - " + city
                        zipp = "<MISSING>"
                        phone = "<MISSING>"
                        hours_of_operation = "<MISSING>"
                        page_url = "<MISSING>"
                        # logger.info(street_address, city, state, location_name)
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                        store = ["<MISSING>" if x == "" else x for x in store]

                        if store[2] in addresses:
                            continue
                        addresses.append(store[2])
                        logger.info("data = " + str(store))
                        logger.info(
                            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                        return_main_object.append(store)

            for a in p.find_all('a'):
                # logger.info(a['href'])
                r_loc = session.get(a['href'], headers=headers)
                soup_loc = BeautifulSoup(r_loc.text, 'lxml')
                # logger.info(soup_loc.prettify())
                page_url = a['href']
                for address in soup_loc.find('section', class_="entry").find_all("div", 'wpb_text_column wpb_content_element'):
                    list_add = list(address.stripped_strings)
                    if list_add != []:
                        # logger.info(list_add)
                        # logger.info(len(list_add))
                        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~")

                        ld = list_add[-1].split()
                        if len(list_add) == 2 and (len(ld) == 3 or len(ld) == 4):
                            # logger.info(list_add[-1].split())
                            # logger.info(len(list_add[-1].split()))
                            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~")
                            street_address = "".join(list_add[0])
                            city1 = " ".join(list_add[1].split()[:-2])
                            city = "".join(city1.replace(',', ''))
                            state = "".join(list_add[1].split()[-2])
                            zipp = "".join(list_add[1].split()[-1])
                            location_name = "Big D - " + city
                            # logger.info(street_address + ' | ' + city + ' | ' +
                            #       state + ' | ' + zipp + ' | ' + location_name)
                        elif len(list_add) == 3:
                            street_address = "".join(list_add[1])
                            city = "".join(list_add[2].split()[:-2])
                            state = "".join(list_add[2].split()[-2])
                            zipp = "".join(list_add[2].split()[-1])
                            location_name = "Big D - " + city

                        elif len(list_add) == 1:
                            street_address = "".join(list_add).split(',')[0]

                            c1 = "".join(list_add).split(',')[1].split()[:-1]
                            city = " ".join(c1)
                            state = "".join(list_add).split(',')[1].split()[-1]
                            zipp = "<MISSING>"
                            location_name = "Big D - " + city
                            # logger.info(city+","+ state+","+location_name)
                        elif len(list_add) == 5:
                            # logger.info(list_add)
                            address = list_add[1].split('services')
                            street_address = address[1].split(
                                'at')[-1].split('in')[0].strip()
                            city = address[1].split(
                                'at')[-1].split('in')[-1].split(',')[0].strip()
                            state = address[1].split(
                                'at')[-1].split('in')[-1].split(',')[-1].replace('.', "").strip()
                            zipp = "<MISSING>"
                            location_name = "".join(address[0]) + " - " + city
                            hours_of_operation = " ".join(list_add[-2:])
                            # logger.info(hours_of_operation)

                        else:

                            if 'Business Hours' == list_add[0]:
                                hours_of_operation = " ".join(list_add).split(
                                    'Amenities')[0].split('Business Hours')[-1].strip()
                            else:
                                hours_of_operation = "<MISSING>"

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                logger.info("data = " + str(store))
                logger.info(
                    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
