import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://www.kort.com//sxa/search/results/?s={8AE60BE8-DF53-49BC-AEAF-CD566CBCEC80}|{A07F1984-B5BC-4E80-90F4-B48D191F4029}&itemid={7BEA850F-986D-4D7D-B189-F82976CCA517}&sig=&autoFireSearch=true&v=%7B919C3870-FD24-4AE3-BC68-E9EBB85E2C4E%7D&p=2000&g=&o=Distance%2CAscending"

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()['Results']

    data = []
    locator_domain = "kort.com"

    for item in stores:

        base = BeautifulSoup(item["Html"],"lxml")
        location_name = base.a.text.strip()
        
        if "brand-kort" not in base.find(class_="loc-result-card-logo").img['src']:
            continue

        raw_address = list(base.find(class_="loc-result-card-address-container").stripped_strings)
        street_address = " ".join(raw_address[:-1]).strip()
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"

        store_number = "<MISSING>"
        phone = base.find(class_="loc-result-card-phone-container").text.strip()
        if phone == "(817) 333-018":
            phone = "(817) 333-0181"

        location_type = ",".join(list(base.find(class_="mobile-container loc-service-list").stripped_strings))
        hours_of_operation = " ".join(list(base.find(class_="mobile-container field-businesshours").stripped_strings))

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"
        
        latitude = item["Geospatial"]["Latitude"]
        longitude = item["Geospatial"]["Longitude"]

        link = "https://www.kort.com/contact/find-a-location" + item["Url"].split("outpatient")[-1]

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
