import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('theshuckinshack_com')





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


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.theshuckinshack.com"
    r = session.get(
        "https://www.theshuckinshack.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for state in soup.find_all("div", {'class': "location-wrapper"}):
        current_state = state.find("h2").text.strip()
        for location in state.find_all("a"):
            if "https://www.theshuckinshack.com/location/easley/" in location["href"]:
                continue
            page_url = location["href"]
           # logger.info(page_url)
            location_request = session.get(location["href"], headers=headers)
            location_soup = BeautifulSoup(location_request.text, "lxml")
            if list(location_soup.find("div", {"class": "flex-column-30"}).find_all("p")[0].stripped_strings) == []:
                continue
            address = list(location_soup.find(
                "div", {"class": "flex-column-30"}).find_all("p")[0].stripped_strings)
            if "," not in address[1]:
                city = address[1]
                zipp = "<MISSING>"
            else:
                # logger.info(address[1])
                city = address[1].split(",")[0]
                if len(address[1].split(",")[1].split(" ")) == 3:
                    zipp = address[1].split(",")[1].split(" ")[2]
                else:
                    zipp = "<MISSING>"
            phone = list(location_soup.find(
                "div", {"class": "flex-column-30"}).find_all("p")[1].stripped_strings)[0]
            hours = " ".join(list(location_soup.find(
                "div", {"class": "flex-column-30"}).find_all("div")[-1].stripped_strings))
            geo_location = location_soup.find(
                "a", text=re.compile("Get Directions"))
            if geo_location != None:
                geo_location1 = location_soup.find(
                    "a", text=re.compile("Get Directions"))["href"]

            store = []
            store.append("http://www.theshuckinshack.com")
            store.append(location.text.strip())
            store.append(address[0].strip())
            store.append(city)
            store.append(current_state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone.replace("easley021@theshuckinshack.com","<MISSING>"))
            store.append("<MISSING>")
            store.append(geo_location1.split(
                "/@")[1].split(",")[0] if "/@" in geo_location1 else "<MISSING>")
            store.append(geo_location1.split(
                "/@")[1].split(",")[1] if "/@" in geo_location1 else "<MISSING>")
            store.append(hours.replace("Â", " ")
                         if hours != "" else "<MISSING>")
            store.append(page_url)
            # logger.info('data===' + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~`')
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
