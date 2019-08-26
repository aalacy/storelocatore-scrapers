import csv
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://rolypoly.com/"
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
    url = 'https://prod-place-picker.herokuapp.com/api/stores/5be8b5d8-e45f-4f63-9063-51c0f89dfec5/kRg3q97L7-H5YLB7hwjl1XzJ75lnso2e'
    driver.get(url)
    listings = json.loads(driver.find_element_by_tag_name("pre").text)['value']

    for listing in listings:
        # id
        location_id.append(listing['_id'])

        # Tile
        locations_titles.append(listing['name'])

        # Phone
        phone_numbers.append(listing['details']['contactInfo']['phoneNumber'])

        # Address
        street_addresses.append(listing['details']['restaurantAddress']['name'].split(',')[0].strip())

        # City
        cities.append(listing['details']['restaurantAddress']['name'].split(',')[1].strip())

        # State
        states.append(listing['details']['restaurantAddress']['name'].split(',')[2].strip().split(' ')[0])

        # Zip
        zip_codes.append(listing['details']['restaurantAddress']['name'].split(',')[2].strip().split(' ')[1])

        # Lat
        latitude_list.append(listing['details']['restaurantAddress']['latitude'])

        # Lon
        longitude_list.append(listing['details']['restaurantAddress']['longitude'])

        # Hour
        hours.append(listing['details']['dineInSchedule'])


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
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                "US",
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