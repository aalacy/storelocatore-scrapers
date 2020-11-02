import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bhotelsandresorts_com')





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

    base_url = "https://www.bhotelsandresorts.com"
    r = session.get("https://www.bhotelsandresorts.com/destinations", headers=headers)
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
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    script_temp = soup.find(id="menu-main").ul
    for script_location in script_temp.find_all('li'):
        location_url = script_location.find('a')['href']

        r1 = session.get(location_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")

        all_scripts = soup1.find_all('script')
        for script in all_scripts:
            if "lng" in str(script):
                script = script.text.split('"places":[')[-1].split('}}')[0]+"}}}"
                break

        address_json = json.loads(script)

        location_name = soup1.find(class_="col span_12 dark").h2.text.strip()
        street_address = address_json['address'].split(",")[0]
        state = address_json['location']['state']
        city = address_json['location']['city']
        zipp = address_json['location']['postal_code']
        if not state:
            city = address_json['address'].split(",")[1].strip()
            state = address_json['address'].split(",")[2].split()[0].strip()
            zipp = address_json['address'].split(",")[2].split()[1].strip()
        latitude = address_json['location']['lat']
        longitude = address_json['location']['lng']
        phone = address_json['content']
        if "-" not in phone:
            phone = "<MISSING>"

        store = [locator_domain, location_url, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
