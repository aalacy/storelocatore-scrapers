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
    base_url = "https://revelatorcoffee.com/pages/locations"

    location_links = []
    

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find(class_="page locations").find_all("p")

    url_list = [data.a.get("href") for data in soup if data.a is not None]
    
    for url in url_list:

        soup = BeautifulSoup(requests.get(url).content, 'html.parser').find("tbody")

        if soup:
            soup = soup.find_all("td")

            for idx, data in enumerate(soup):
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

                if (idx % 2) > 0:
                    contents = data.contents
                    locator_domain = url

                    if len(contents) == 7:
                        location_name = contents[1].get_text()

                        address = contents[3].contents
                    else:
                        location_name = contents[3].get_text()

                        address = contents[5].contents

                    if len(address) == 3:
                        street_address = address[0]
                        city_state_zip = address[2]
                        city = city_state_zip.split(', ')[0]
                        state = city_state_zip.split(', ')[1].split(' ')[0]
                        zip = city_state_zip.split(', ')[1].split(' ')[1]
                    else:
                        if location_name.find("Marietta") > -1:
                            addr = address[0].contents
                            street_address = addr[0].split(',')[0]
                            city = street_address.split(' ')[4]
                            street_address = street_address.split(city)[0]
                            state_zip = addr[0].split(',')[1].lstrip()
                            state = state_zip.split(' ')[0]
                            zip = state_zip.split(' ')[1]
                        else:
                            addr = contents[9].contents
                            street_address = addr[0].get_text()
                            city_state_zip = addr[1].split(', ')

                            city = city_state_zip[0]
                            state = city_state_zip[1].split(' ')[0]
                            zip = city_state_zip[1].split(' ')[1]

                    hours_of_operation = "<INACCESSIBLE>"
                    
                    location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
        else:
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

            soup = BeautifulSoup(requests.get(url).content, 'html.parser').find(class_="Index-page-content")
            address = soup.find_all(class_="")[1].contents
            street_address = address[0]
            city_state_zip = address[2]
            city = city_state_zip.split(', ')[0]
            state = city_state_zip.split(', ')[1].split(' ')[0]
            zip = city_state_zip.split(', ')[1].split(' ')[1]
            location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
