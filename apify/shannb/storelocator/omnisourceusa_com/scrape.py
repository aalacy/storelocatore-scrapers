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
    base_url = "https://www.omnisourceusa.com/locations"

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

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find_all(class_="contact-card-info")

    for content in soup:

        location_name = content.find(class_="contact-card-name").get_text().replace("\r\n", '').replace(" ", '')
        address = content.find(class_="contact-card-small").contents

        city_state_zip = None

        if len(address) > 11:
            street_address = address[0].lstrip().replace("\r\n", '')
            street_address = street_address + address[2].lstrip().replace("\r\n", '')
            city_state_zip = address[4].replace("\r\n", '').lstrip(' ')
            phone = address[7].get_text()
        else:
            street_address = address[0].lstrip().replace("\r\n", '')
            city_state_zip = address[2].replace("\r\n", '').lstrip(' ')
            phone = address[5].get_text()
        
        
        city = city_state_zip.split(',')[0].replace(',', '')
        state = city_state_zip.split(',')[1].lstrip(' ').split(' ')[0]
        zip = city_state_zip.split(',')[1].lstrip(' ').split(' ')[1]
        

        location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
