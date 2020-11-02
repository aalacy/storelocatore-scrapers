

import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('scramblersrestaurants_com')



session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://scramblersrestaurants.com/"
    r =  session.get("https://scramblersrestaurants.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1584183158713", headers=headers)
    soup = BeautifulSoup(r.text, "lxml") 
    for data in soup.find("store").find_all("item"):
        location_name = data.find('location').text
        addr = BeautifulSoup(data.find('description').text, "lxml")
        address = list(addr.find("div").stripped_strings)
        if len(address) == 2:
            street_address = address[0]
            city = address[1].split(",")[0]
            state = address[-1].split(",")[1].split("\xa0")[0].strip()
            zipp = address[-1].split(",")[1].split("\xa0")[-1].strip()
        else:
            if "\xa0" in address[0]:
                street_address = address[-1].split(",")[0].split("\xa0")[0]
                city = address[0].split(",")[0].split("\xa0")[1]
                state = address[-1].split(",")[1].split(" ")[1].replace("OH\xa043606","OH")
                zipp = address[-1].split(",")[1].split(" ")[-1].replace("OH\xa043606","43606")
            else:
                addr1 = address[0].replace("12455 W Capitol Dr, Unit C, Brookfield, WI 53005","12455 W Capitol Dr Unit C Brookfield, WI 53005").replace("6313 Pullman Dr., Lewis Center","6313 Pullman Dr. Lewis Center,")
                street_address = " ".join(addr1.split(",")[0].split(" ")[:-1]).replace("Lewis","").strip()
                city = addr1.split(",")[0].split(" ")[-1].replace("Center","Lewis Center")
                state = addr1.split(",")[-1].split(" ")[1]
                zipp = addr1.split(",")[-1].split(" ")[2]
        hours = "Open Daily 6:30am-3:00pm"
        latitude = data.find('latitude').text
        longitude = data.find("longitude").text
        phone = data.find("telephone").text


        store = []
        store.append(base_url)
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
        store.append(hours)
        store.append("<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # logger.info("data===="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
