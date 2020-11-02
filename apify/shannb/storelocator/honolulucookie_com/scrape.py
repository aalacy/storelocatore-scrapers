import csv
import requests
from bs4 import BeautifulSoup
import re

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
    base_url = "https://www.honolulucookie.com/content/store-locations.asp"

    location_links = []
    
    locator_domain = base_url
    country_code = 'US'

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find_all(class_="location-section")
    url_list = []

    for location_section in soup:

        if location_section.h3.get_text().find("Customer Service") > -1:
            location_type = "Customer Service & Executive Offices"
            locator_domain = base_url
            location_type = "<MISSING>"
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            for location in location_section.find_all("ul"):
                contents = location.contents
                location_name = contents[1].get_text()
                hours_of_operation = ''
                for data in contents:
                    
                    if data == "\n":
                        continue

                    phone_match = re.search("Phone:|Ph:", data.get_text())
                    hours_match = re.search("Mon|Tue|Wed|Thur|Fri|Sat|Sun", data.get_text())
                    if phone_match:
                        phone = data.get_text()
                    elif hours_match:
                        hours_of_operation += data.get_text() + ' '

                location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

        
        else:
            for location in location_section.find_all("ul"):
                location_name = None
                locator_domain = None
                location_type = "<MISSING>"
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zip = "<MISSING>"
                store_number = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>" 
                hours_of_operation = ''
                for idx, data in enumerate(location.contents):
                
                    if data == '\n':
                        continue
                    elif idx == 1:
                        location_name = data.get_text()
                        if data.a:
                            locator_domain = " https://www.honolulucookie.com/" + data.a.get("href")
                        else:
                            locator_domain = "<MISSING>"
                    else:

                        phone_match = re.search("Phone:|Ph:", data.get_text())
                        hours_match = re.search("Mon|Tue|Wed|Thur|Fri|Sat|Sun", data.get_text())
                        fax_match = re.search("Fax:", data.get_text())
                        if phone_match:
                            phone = data.get_text()
                            phone_found = True
                        elif hours_match:
                            hours_of_operation += data.get_text() + ' '
                        elif fax_match:
                            continue
                        elif len(data.get_text().split(', ')) > 1:
                            city_state_zip = data.get_text().split(', ')
                            city = city_state_zip[0]
                            state = city_state_zip[1].split(' ')[0]
                            zip = city_state_zip[1].split(' ')[1]
                        else:
                            street_address += data.get_text() + ' '
                location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    partner_store_url = 'https://www.honolulucookie.com/content/other-retailers.asp'
    
    soup = BeautifulSoup(requests.get(partner_store_url).content, 'html.parser').find_all(class_="store-locations")

    for data in soup:
         stores = data.find_all("p")

         for store in stores:
            location_type = "Partner Store"
            locator_domain = partner_store_url
            street_address = ""
            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

            store = store.contents

            for idx, info in enumerate(store):

                phone_match = re.search("Phone:|Ph:", info)
                if idx == 1:
                    location_name = info.get_text()
                elif len(info.split(', ')) > 1:
                    city_state_zip = info.split(', ')
                    city = city_state_zip[0]
                    state = city_state_zip[1].split(' ')[0]
                    zip = city_state_zip[1].split(' ')[1]
                elif phone_match:
                    phone = phone_match.group(0)
                else:
                    street_address =+ info + ' '
            
            location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
