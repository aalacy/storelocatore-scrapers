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
    base_url = "https://www.micasitarestaurants.com/locations"

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

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser')

    restaurant_names = soup.find_all(class_="style-jv6v9vso1imageItemtitle")
    restaurant_addresses = soup.find_all(class_="style-jv6v9vso1imageItemdescription")

    for num, value in enumerate(restaurant_names):

        location_name = restaurant_names[num].get_text()            
        address = restaurant_addresses[num].contents
        
        store_number = location_name.split('#')[1]

        match = re.search('Rd.?|St.?|Blvd.?|Ctr.|Ln.?|Pkwy.?', address[0])
        
        if match is not None:
            match_idx = match.span()[1]
            separator = match.group(0)
            street_address = address[0][:match_idx]

            if address[0][match_idx:] != '':
                city_state = address[0][match_idx:].split(', ')
                city = city_state[0]
                state = city_state[1]
            else:
                city = "<MISSING>"
                state = "<MISSING>"
        else:
            street_address = "<MISSING>"
            city_state = address[0].split(', ')
            city = city_state[0]

            if len(city_state) > 1:
                state = city_state[1]
            else:
                state = "<MISSING>"
        
        phone = address[2]

        location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
