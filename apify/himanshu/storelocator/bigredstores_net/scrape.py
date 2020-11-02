import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import  pprint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bigredstores_net')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

#####  branches  ######


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://bigredstores.net/"

    addresses = []
    result_coords = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""

    location_url = "https://bigredstores.net/findus/"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # logger.info(soup.prettify())
    for link in soup.find_all("div", class_="has-post-thumbnail"):
        list_add = list(link.stripped_strings)
        street_address = list_add[0].strip()

        city = list_add[-1].strip()
        page_url = link.a['href']
        r_loc = session.get(link.a['href'], headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        try:
            coords = soup_loc.find("div", class_="et_pb_map_pin")
            if coords == None:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                latitude = coords["data-lat"]
                longitude = coords["data-lng"]
            content = list(soup_loc.find_all(
                "div", class_="et_pb_tab_content")[1].stripped_strings)

            if "|" not in " ".join(content):

                if len(content) > 2:
                    location_name = content[0].strip()
                    state = content[2].split(',')[1].split()[0].strip()
                    zipp = content[2].split(',')[1].split()[-1].strip()
                    phone_list = re.findall(re.compile(
                        ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(content[-1]))
                    if phone_list:
                        phone = phone_list[-1]
                    else:
                        phone = "<MISSING>"
                    # phone = content[-1].strip()
                else:
                    location_name = "<MISSING>"
                    state = content[-1].split(',')[1].split()[0].strip()
                    zipp = content[-1].split(',')[1].split()[-1].strip()
                    phone = "<MISSING>"
                # logger.info(phone)
            else:
                location_name = "<MISSING>"
                state = content[-1].split(',')[1].split()[0].strip()
                zipp = content[-1].split(',')[1].split()[-1].strip()
                phone = "<MISSING>"

        except:
            location_name = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            phone = "<MISSING>"
        # logger.info(phone)
        if "72015" in phone:
            # logger.info(phone)
            phone = "<MISSING>"
        if "3544 Airport Road, Pearcy, AR" in street_address:
            street_address = list_add[0].split(',')[0].strip()
            city = list_add[0].split(',')[1].strip()
            state = list_add[0].split(',')[-1].strip()
            zipp = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone.replace("\t", " "), location_type, latitude, longitude, hours_of_operation, page_url]

        if store[2] in addresses:
            continue
        addresses.append(store[2])

        store = [x.encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        # logger.info("data = " + str(store))
        # logger.info(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
