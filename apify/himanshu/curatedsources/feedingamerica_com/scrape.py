
import csv
import time

import requests
from bs4 import BeautifulSoup
from lxml import etree
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('feedingamerica_com')




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

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.feedingamerica.org"
    addresses = []

    r = request_wrapper("https://ws2.feedingamerica.org/fawebservice.asmx/GetAllOrganizations","get", headers=headers)
    # tree = etree.parse(r.text)
    # soup = BeautifulSoup(r.text, "html.parser")
    soup = BeautifulSoup(r.text, "xml")

    for loc_detail in soup.find_all("Organization"):

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
        page_url = ""

        # do your logic here.
        store_number = loc_detail.find("OrganizationID").next
        location_name = loc_detail.find("FullName").next
        phone = loc_detail.find("Phone").next
        street_address = loc_detail.find("MailAddress").find("Address1").next
        # street_address = street_address + loc_detail.find("MailAddress").find("Address2").next
        if "PO Box" in street_address:
            street_address = "".join(street_address[:street_address.index("PO Box")])
        city = loc_detail.find("MailAddress").find("City").next
        state = loc_detail.find("MailAddress").find("State").next
        zipp = loc_detail.find("MailAddress").find("FullZip").next
        latitude = loc_detail.find("MailAddress").find("Latitude").next
        longitude = loc_detail.find("MailAddress").find("Longitude").next

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) not in addresses and store[2] and country_code:
            addresses.append(str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


        for pod_item in loc_detail.find_all("PDO"):
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            store_number = ""
            phone = ""
            location_type = ""
            raw_address = ""
            hours_of_operation = ""
            latitude = ""
            longitude = ""
            page_url = ""

            # do your logic here.
            location_name = pod_item.find("Title").next
            phone = pod_item.find("Phone").next
            street_address = pod_item.find("Address").next
            if "PO Box" in street_address:
                street_address = "".join(street_address[:street_address.index("PO Box")])
            city = pod_item.find("City").next
            state = pod_item.find("State").next
            zipp = pod_item.find("ZipCode").next
            page_url = pod_item.find("Website").next.strip()

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) not in addresses and store[2] and country_code:
                addresses.append(str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
