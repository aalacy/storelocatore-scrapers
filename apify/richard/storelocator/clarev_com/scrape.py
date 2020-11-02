from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

COMPANY_URL = 'https://www.clarev.com/'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow([
            "locator_domain",
            "page_url",
            "location_name",
            "street_address",
            "city",
            "state",
            "zip",
            "country_code",
            "store_number",
            "phone",
            "location_type",
            "latitude",
            "longitude",
            "hours_of_operation"
        ])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    latitude_list = []
    longitude_list = []
    phone_numbers = []
    hours = []
    data = []

    location_url = 'https://www.clarev.com/pages/locations'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    req = session.get(location_url, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    locations = base.find_all(class_='grid__item store-block large--one-half medium--one-half small--one-whole padding-left')

    for location in locations:
        location_title = location.find('h1').text.strip()
        phone_number = location.find(class_='grid__item one-half small--one-whole small--text-left').p.text.split('\n')[0].strip()
        street_address = location.find(class_='text-style-capitalize').text.split('\n')[0]
        city = location.find(class_='text-style-capitalize').text.split('\n')[1].split(',')[0]
        state = location.find(class_='text-style-capitalize').text.split('\n')[1].split(',')[1].strip().split(' ')[0]
        zip_code = location.find(class_='text-style-capitalize').text.split('\n')[1].split(',')[1].strip().split(' ')[1]
        hour = location.find(class_='grid__item one-half small--one-whole small--text-left text-right').find_all("p")[-1].text.replace("\n"," ").strip()
        if " time" in hour:
            hour = hour[hour.find(" time")+5:].strip()
        hour = (re.sub(' +', ' ', hour)).strip()
        map_link = location.h3.a["href"]
        try:
            if map_link != '':
                latitude = re.search('([-+]?)([\d]{1,3})(((\.)(\d+)())),([-+]?)([\d]{1,3})(((\.)(\d+)()))',map_link).group(0).split(',')[0]
                longitude = re.search('([-+]?)([\d]{1,3})(((\.)(\d+)())),([-+]?)([\d]{1,3})(((\.)(\d+)()))',map_link).group(0).split(',')[1]
            else:
                latitude = '<MISSING>'
                longitude = '<MISSING>'
        except:
            latitude = '<MISSING>'
            longitude = '<MISSING>'

        # Store data
        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        latitude_list.append(latitude)
        longitude_list.append(longitude)
        phone_numbers.append(phone_number)
        hours.append(hour)

    # Store data
    for locations_title, street_address, city, state, zipcode, phone_number, latitude, longitude, hour in zip(locations_titles, street_addresses, cities, states, zip_codes, phone_numbers, latitude_list, longitude_list, hours):
        data.append([
            COMPANY_URL,
            location_url,
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            'US',
            '<MISSING>',
            phone_number,
            '<MISSING>',
            latitude,
            longitude,
            hour,
        ])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
