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
    base_url = "https://www.bigairusa.com"

    location_links = []
    location_name = None
    locator_domain = None
    street_address = None
    city = None
    state = None
    zip = None
    country_code = None
    store_number = "<MISSING>"
    phone = None
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = None

    for i, block in enumerate(BeautifulSoup(requests.get(base_url).content, 'html.parser').find_all(class_="fusion-text")):

        if i > 1:
            break

        li_tags = block.find_all("li")

        for li in li_tags:
            link = li.a.get('href')
            soup = BeautifulSoup(requests.get(link).content, 'html.parser')
            address = soup.find(class_="contact-info-container").find(class_="address")
            
            if address:
                street_address = address.string.split(" I ")[0]
                city = address.string.split(" I ")[1].split(", ")[0]
                state = address.string.split(" I ")[1].split(", ")[1]
                zip = address.string.split(" I ")[2]
                country_code = "US"
            else:
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zip = "<MISSING>"
                country_code = "<MISSING>"
            location_name = city

            phone = soup.find(class_="phone")
            locator_domain = link
            
            

            hours_link = soup.find(id="menu-item-1105").a.get("href")
            hours = BeautifulSoup(requests.get(hours_link).content, 'html.parser').find_all(class_="fusion-text")[1]

            for i, child in enumerate(hours.find_all("li")):
                if i ==0:
                    hours_of_operation = child.get_text() 
                else:
                    hours_of_operation = hours_of_operation + ", " + child.get_text()
                

            location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
