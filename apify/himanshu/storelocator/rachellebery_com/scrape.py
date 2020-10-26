import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rachellebery_com')



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
    base_url = "https://www.rachellebery.com"
    r = session.get("https://www.rachellebery.ca/trouver-un-magasin/", headers=headers)
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
    location_type = "rachellebery"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    datapath_url = soup.text.split('datapath":"')[1].split('"')[0].replace("\\", "")
    # logger.info("datapath_url === " + datapath_url)
    r1 = session.get(datapath_url, headers=headers)
    json_data = r1.json()
    arr_street_address = []
    for data in json_data:
        if data["address"] in street_address:
            continue
        latitude = data["lat"]
        longitude = data["lng"]
        street_address = data["address"]
        arr_street_address.append(street_address)
        city = data["city"]
        location_name = city
        state = data["state"]
        zipp = data["postal"]
        phone = data["phone"]
        country_code = 'CA'
        day_list = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        hoursfrom_list = data["hours1"].split(',')
        hoursto_list = data["hours2"].split(",")
        hours_of_operation = ""
        for i in range(len(day_list)):
            hours_of_operation += day_list[i] + " : " + hoursfrom_list[i] + "-" + hoursto_list[i] + ", "
        hours_of_operation = hours_of_operation[:-2]
        # logger.info(" === data ==== " + str(hours_of_operation))
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
