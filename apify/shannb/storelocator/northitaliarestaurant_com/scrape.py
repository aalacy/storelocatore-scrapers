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
    base_url = "https://www.northitaliarestaurant.com/locations/"

    location_links = []
    
    locator_domain = base_url
    country_code = 'US'

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find_all(class_="location-state")
    url_list = []

    for link_group in soup:

        if link_group == '\n':
            continue
        else:
            [ url_list.append(data.a.get("href")) for data in link_group.contents if data != '\n']

    
    for url in url_list:
        location_name = None
        street_address = None
        city = None
        state = None
        zip = "<MISSING>"
        
        store_number = "<MISSING>"
        phone = None
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        locator_domain = url
        soup = BeautifulSoup(requests.get(url).content, 'html.parser').find(class_="locations-map-content")
        
        address = soup.address.span.contents

        if len(address) > 1:
            street_address = address[0]

            city_state_zip = address[2].split(',')
            city = city_state_zip[0]
            state = city_state_zip[1].split(' ')[1]
            zip = city_state_zip[1].split(' ')[2]

            if soup.find(class_="location-phone").a:
                phone = soup.find(class_="location-phone").a.get_text()
            else:
                phone = "<MISSING>"
            location_name = city

            hours = [hours.li.get_text() for hours in soup.find_all(class_="location-hours")]
        
            if len(hours):
                hours_concat = ''
                for hour in hours:
                    hours_concat = hours_concat + " " + hour

                hours_of_operation = hours_concat
        else:
            city = address[0].split(' ')[0].strip(',')
            state = address[0].split(' ')[1]
            street_address = "<MISSING>"
            location_name = city
            phone = "<MISSING>"

        location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
