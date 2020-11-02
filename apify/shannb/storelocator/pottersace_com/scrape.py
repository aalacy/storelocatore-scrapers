import csv
import requests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    location_list = []
    base_url = "http://pottersace.com/page.asp?p=Store%20Locator"

    location_links = []
    location_name = None
    locator_domain = base_url
    street_address = None
    city = None
    state = None
    zip = "<MISSING>"
    country_code = 'US'
    store_number = "<MISSING>"
    phone = None
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find_all('table')[4].contents

    for content in soup:

        if content == '\n':
            continue

        elif len(content.contents) > 1:

            location_name = content.td.get_text()
            city = location_name
            street_address = content.contents[2].get_text()
            phone = content.contents[6].get_text()
            latlong = content.contents[8].a.get("href").split("ll=")
            
            if len(latlong) > 1:

                if len(latlong[1].split("&spn")) == 1:
                    latlong = latlong[1].split("&sspn")[0]
                else:
                    latlong = latlong[1].split("&spn")[0]
            
                latitude = latlong.split(',')[0]
                longitude = latlong.split(',')[1]

            location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

        elif len(content.contents) == 1:
            state = content.contents[0].get_text().split(' ')[0]

        else:
            continue
            

    #
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
