import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('branns_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    base_url = "https://www.branns.com"
    link = "https://www.branns.com/locations/"
    r = session.get(link, headers=headers)
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

    for script in soup.find_all('div', {'class': re.compile('et_pb_module et_pb_text et_pb_text')}):
        list_store_data = list(script.stripped_strings)

        if len(list_store_data) > 2 and "hours" in str(list_store_data).lower():
            location_name = list_store_data[0].encode("ascii", "replace").decode().replace("?","'")
            street_address = list_store_data[1]
            phone = list_store_data[3]
            hours_of_operation = ",".join(list_store_data[4:]).replace("","").replace("Hours:","").replace(","," ").encode("ascii", "replace").decode().replace("?","-").strip()
            if "Kitchen" in hours_of_operation:
                hours_of_operation = hours_of_operation[:hours_of_operation.find("Kitchen")].strip()
            country_code = 'US'

            city = list_store_data[2].split(',')[0]
            if len(list_store_data[2].split(',')[1].strip().split(' ')) > 1:
                zipp = list_store_data[2].split(',')[1].strip().split(' ')[-1]
                state = list_store_data[2].split(',')[1].strip().split(' ')[-2]
            else:
                zipp = list_store_data[2].split(',')[1].strip().split(' ')[-1]
                state = '<MISSING>'
            if "MI" in city:
                city = city.replace("MI","").strip()
                state = "MI"
        elif "@" in str(script):
            map_location = script.find('a')['href']
            latitude = map_location.split("/@")[1].split(",")[0]
            longitude = map_location.split("/@")[1].split(",")[1]

            store = [locator_domain, link, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
