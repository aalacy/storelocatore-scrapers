import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('wetzels_com')






session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
    }

    addresses = []
    base_url = "http://www.wetzels.com"

    r = session.get("https://www.wetzels.com/find-a-location", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

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
    page_url = "https://www.wetzels.com/find-a-location"

    projectid = soup.find("ul", {"id": "ctl01_ucMenuItems_ulNavMenus"})["projectid"]
    sitepageid = soup.find("div", {"id": "ctl01_modLocationLocator"})["data-sitepagemoduleid"]
    json_body = '{"method":"GetLocationLocator","format":"json","parameters":"ProjectID=' + projectid + '&SitePageModuleID=' + sitepageid + '&Latitude=&Longitude=","typefields":[{"DataType":"LocationLocatorRow","Columns":"*"}],"host":"websiteoutput"}'
    r_json = session.post("https://websiteoutputapi.mopro.com/WebsiteOutput.svc/api/get",
                           headers=headers,
                           data=json_body)
    json_data = r_json.json()

    for location_data in json_data[1]["rows"]:
        # logger.info("location_data === "+ str(location_data))
        location_name = location_data["Name"]
        street_address = ", ".join(list(BeautifulSoup(location_data["Address"],"lxml").stripped_strings))
        phone = location_data["Telephone"]
        latitude = location_data["Latitude"]
        longitude = location_data["Longitude"]
        if latitude == "0.0000000000":
            latitude = "<MISSING>"
        if longitude == "0.0000000000":
            longitude = "<MISSING>"
        location_type = ",".join(location_data["LocationTypes"])
        us_zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(location_data["City"]))
        ca_zipp_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(location_data["City"]))

        if us_zipp_list:
            zipp = us_zipp_list[-1]
            country_code = "US"
        elif ca_zipp_list:
            zipp = ca_zipp_list[-1]
            country_code = "CA"
        else:
            country_code = "US"
            zipp = ""

        state_list = re.findall(r' ([A-Z]{2}) ', location_data["City"])
        if state_list:
            state = state_list[-1]
        else:
            state = ""

        if zipp and state:
            city = location_data["City"].replace(zipp,"").replace(state,"").replace(",","").strip()
        else:
            city = location_data["City"].split(",")[0]
            if len(location_data["City"].split(",")[1].strip().split(" ")) > 2:
                state = " ".join(location_data["City"].split(",")[1].strip().split(" ")[:-1])
            else:
                state = location_data["City"].split(",")[1].strip().split(" ")[0]
        if state == "Bahamas":
            continue
        state = state.replace("S7H","").replace("CA San","CA").replace("CCA","CA").strip()
        if street_address == "2500 University Dr. NW":
            state = "AB"
        # logger.info("zipp ==== " + str(zipp))
        # logger.info("state ==== " + str(state))
        # logger.info("city ==== " + str(city))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses and "coming soon" not in location_name.lower():
            addresses.append(str(store[1]) + str(store[2]))

            store = [x.strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
