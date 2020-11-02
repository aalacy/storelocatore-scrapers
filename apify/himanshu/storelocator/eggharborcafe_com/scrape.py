import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('eggharborcafe_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.eggharborcafe.com"
    url = "https://eggharborcafe.com/locations/"

    response = session.get( url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    for link in soup.find_all("a", text=re.compile("view location")):
        r_loc = session.get(link["href"], headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        location_name = link["href"].split(
            "/")[-2].capitalize().replace("-", " ").strip()
        address = " ".join(list(soup_loc.find(
            "div", {"id": "location_address"}).stripped_strings)).split(",")
        street_address = " ".join(address[:-2]).strip()
        city = address[-2]
        state = address[-1].split()[0].strip()
        zipp = address[-1].split()[-1].strip()
        phone = soup_loc.find("p", {"id": "location_phone"}).text.strip()
        hours_of_operation = " ".join(
            list(soup_loc.find("p", {"id": "location_hours"}).stripped_strings)).replace("Hours:", "").strip()
        store_type = "<MISSING>"
        store_number = "<MISSING>"
        try:
            response = session.get( link["href"], headers=headers)
            soup = BeautifulSoup(response.text, "lxml")
            latitude = (soup.find("script",{"id":"wpgmaps_core-js-extra"}))
            data_crood = (str(latitude).split("var wpgmaps_localize =")[1].split("var wpgmaps_localize_mashup_ids =")[0].replace("}};","}}"))
            json_data = json.loads(data_crood)
            data_id = str(latitude).split('var wpgmaps_localize_cat_ids = {"')[1].split('":"')[0]
            latitude = (json_data[str(data_id)]['map_start_lat'])
            longitude = (json_data[str(data_id)]['map_start_lng'])
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        page_url = link["href"]

        store = []
        store.append("https://www.eggharborcafe.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        # logger.info("data == " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
