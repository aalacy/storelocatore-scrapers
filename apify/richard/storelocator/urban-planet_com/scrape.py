import csv
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://urban-planet.com"
CHROME_DRIVER_PATH = "chromedriver"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_titles = []
    location_id = []
    street_addresses = []
    cities = []
    states = []
    countries = []
    zip_codes = []
    phone_numbers = []
    hours = []
    longitude_list = []
    latitude_list = []
    data = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    url = 'https://urban-planet.com/apps/api/v1/stores?&_=1566796612344'
    driver.get(url)
    listings = json.loads(driver.find_element_by_tag_name("pre").text)['stores']

    for listing in listings:
        # Location code
        location_id.append(listing['store_code'])

        # Title
        locations_titles.append(listing['address']['name'])

        # Address
        street_addresses.append((listing['address']['line1'] + ' ' + (listing['address']['line2'] if listing['address']['line2'] else '') + ' ' + (listing['address']['line3'] if listing['address']['line3'] else '')).strip() if (str(listing['address']['line1']) + ' ' + str(listing['address']['line2']) + ' ' + str(listing['address']['line3'])).strip() != '' else '<MISSING>')

        # City
        cities.append(listing['address']['city'])

        # state
        states.append(listing['address']['state_code'].strip() if listing['address']['state_code'] else '<MISSING>')

        # Country
        countries.append(listing['address']['country_code'])

        # Zip
        zip_codes.append(listing['address']['zip'])

        # Lat
        latitude_list.append(listing['address']['latitude'])

        # Lon
        longitude_list.append(listing['address']['longitude'])

        # hours
        hours.append(listing['open_hours'])

        # Phone
        phone_numbers.append(listing['phone'])

    for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            latitude,
            longitude,
            hour,
            id,
            country
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours,
        location_id,
        countries
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                country,
                id,
                phone_number,
                "<MISSING>",
                latitude,
                longitude,
                hour,
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()