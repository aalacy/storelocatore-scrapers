from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv

import re
from sgselenium import SgChrome
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('medicineshoppe_ca')


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    driver = SgChrome().chrome()

    data = []
    found = []
    locator_domain = "medicineshoppe.ca"

    ca_list = ["AB", "BC", "SK", "NS", "MB", "QC", "ON", "NT", "PE", "NL", "NU", "YT"]

    for i in ca_list:

        url = "https://www.medicineshoppe.ca/en/find-a-store?ad=%s" %i

        logger.info(i)
        driver.get(url)

        base = BeautifulSoup(driver.page_source,"lxml")

        store_list = base.find(class_="search-list").find_all(class_="details")
        
        for st in store_list:
            link = "https://www.medicineshoppe.ca" + st['href']
            if link in found:
                continue
            found.append(link)

            logger.info(link)

            req = session.get(link, headers = HEADERS)
            base = BeautifulSoup(req.text,"lxml")

            location_name = base.h1.text.strip()
            try:
                store_number = location_name.split("#")[1].replace("(N)","")
            except:
                store_number = "<MISSING>"

            try:
                location_type = ", ".join(list(base.find(class_="pharmacy-general-services editable single").ul.stripped_strings))
            except:
                location_type = "<MISSING>"

            address = base.address.text.strip().split(",")
            
            if len(address) == 4:
                street_address,city,state,zipcode = address
            state = state.replace("(","").replace(")","").strip()
            city = city.strip()
            street_address = street_address.strip()
            zipcode = zipcode.strip()

            try:
                phone = base.find("div",attrs={"class":"columns medium-12 large-6 pharmacy-content-infos"}).find("a").text
            except:
                phone = "<MISSING>"
            hours_of_open = base.find("div",attrs={"class":"table-hours-container"}).find_all("tr")
            
            for t in range(len(hours_of_open)):
                hours_of_open[t] = ' : '.join([h.text for h in hours_of_open[t].find_all("td")])
            hours_of_open = " ".join(hours_of_open)

            try:
                map_str = str(base.find(class_="pharmacy-map-background"))
                latitude , longitude = re.findall(r'[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+', map_str)[0].split(",")
            except:
                latitude = longitude = "<MISSING>"
            country_code = "CA"

            data.append([locator_domain, link, location_name, street_address, city, state, zipcode, country_code, store_number, phone, location_type, latitude, longitude, hours_of_open])

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
