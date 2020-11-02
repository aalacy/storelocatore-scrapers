import csv
import requests
from bs4 import BeautifulSoup
import xlsxwriter
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def add_store(locator_domain, location_name, street_address, city, state, zip, phone, latitude, longitude):

    country_code = "US"
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    barre_store = [locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
    return barre_store


def fetch_data():
    # Your scraper here
    base_url = 'https://www.barresoul.com'

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find(class_="folder")

    locations = soup.div.contents

    location_urls = []

    barre_stores = []

    for location in locations:

        if location == '\n':
            continue
        elif location.get_text().find("Account Login") > -1:
            break;

        soup = BeautifulSoup(requests.get(base_url+location.a.get("href")).content, 'html.parser')

        locator_domain = base_url+location.a.get("href")

        if len(soup.title.get_text().split(",")) > 1:
            location_name = soup.title.get_text().split(",")[0]
        else:
            location_name = soup.title.get_text().split("|")[0].strip(" ")
        street_address = None
        addtl_address = None

        lat_long = None
        if soup.find(class_="sqs-block map-block sqs-block-map sized vsize-7"):
            lat_long = json.loads(soup.find(class_="sqs-block map-block sqs-block-map sized vsize-7")['data-block-json'])['location']
        elif soup.find(class_="sqs-block map-block sqs-block-map sqs-col-5 span-5 float float-right"):
            lat_long = json.loads(soup.find(class_="sqs-block map-block sqs-block-map sqs-col-5 span-5 float float-right")['data-block-json'])['location']
        elif soup.find(class_="sqs-block map-block sqs-block-map sqs-col-6 span-6 float float-right"):
            lat_long = json.loads(soup.find(class_="sqs-block map-block sqs-block-map sqs-col-6 span-6 float float-right")['data-block-json'])['location']
        elif soup.find(class_="sqs-block map-block sqs-block-map sqs-col-5 span-5 float float-right sized vsize-7"):
            lat_long = json.loads(soup.find(class_="sqs-block map-block sqs-block-map sqs-col-5 span-5 float float-right sized vsize-7")['data-block-json'])['location']

        
        latitude = lat_long['mapLat']
        longitude = lat_long['mapLng']


        if location_name == "Portsmouth":

            address = soup.find_all("h3")[2].contents

            for i, val in enumerate(address):

                if i == 0:
                    street_address = val
                elif i == 2:
                    city = val.split(",")[0]
                    state = val.split(",")[1].strip(" ")
                elif i == 3:
                    zip = val.string
            phone = soup.find_all("h3")[2].next_sibling.contents[0].string
            barre_store = add_store(locator_domain, location_name, street_address, city, state, zip, phone, latitude, longitude)
            barre_stores.append(barre_store)
        elif location_name == "Wayland Square":
            address = soup.find_all("h3")[2].contents

            street_address = address[1].strip("\xa0")
            city = address[3].split(" ")[0].strip(",")
            state = address[3].split(" ")[1]
            zip = address[3].split(" ")[2]
            phone = soup.find_all("h3")[2].next_sibling.contents[0].string.strip(" \xa0| \xa0")
            barre_store = add_store(locator_domain, location_name, street_address, city, state, zip, phone, latitude, longitude)
            barre_stores.append(barre_store)
        elif soup.find_all("h3")[2].strong is None:
            address1 = soup.find_all("h3")[2].next_sibling.children

            for i, val in enumerate(address1):

                if i == 0:
                    street_address = val.string
                elif i == 2:
                    addtl_address = val.string

            city = addtl_address.split(" ")[0].strip(",")
            state = addtl_address.split(" ")[1].strip(", ")
            zip = addtl_address.split(" ")[2]
            phone = soup.find_all("h3")[2].next_sibling.next_sibling.next_sibling.next_sibling.contents[0].strip(" |")

            barre_store = add_store(locator_domain, location_name, street_address, city, state, zip, phone, latitude, longitude)
            barre_stores.append(barre_store)

            address2 = soup.find_all("h3")[2].next_sibling.next_sibling.children

            for i, val in enumerate(address2):

                if i == 0:
                    street_address = val.string
                elif i == 2:
                    addtl_address = val.string

            city = addtl_address.split(" ")[0].strip(",")
            state = addtl_address.split(" ")[1].strip(", ")
            zip = addtl_address.split(" ")[2]

            barre_store = add_store(locator_domain, location_name, street_address, city, state, zip, phone, latitude, longitude)
            barre_stores.append(barre_store)

        else:
            address = soup.find_all("h3")[2].strong.children

            for i, val in enumerate(address):
                if i == 0:
                    street_address = val
                else:
                    addtl_address = val
                

            city = addtl_address.split(" ")[0].strip(",")
            state = addtl_address.split(" ")[1].strip(", ")
            zip = addtl_address.split(" ")[2]
            phone = soup.find_all("h3")[2].next_sibling.contents[0].string.strip(" \xa0| \xa0")
            barre_store = add_store(locator_domain, location_name, street_address, city, state, zip, phone, latitude, longitude)
            barre_stores.append(barre_store)

    return barre_stores
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
