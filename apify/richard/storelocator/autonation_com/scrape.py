import csv
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.autonation.com"
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
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = "https://www.autonation.com/StoreDetails/Get/?lat=33.84502410888672&long=-84.37747192382812&radius=10000&zipcode=30305&instart_disable_injection=true"
    driver.get(store_url)

    locations = json.loads(driver.find_element_by_css_selector("pre").text)["Store"]

    for location in locations:
        # ID
        location_id.append(location["StoreId"])

        # Title
        locations_titles.append(location["Name"])

        # Street address
        street_addresses.append(
            location["AddressLine1"] + " " + location["AddressLine2"]
        )

        # City
        cities.append(location["City"])

        # State
        states.append(location["StateCode"])

        # Phone
        phone_numbers.append(location["Phone"])

        # Zip
        zip_codes.append(location["PostalCode"])

        # Latitude
        latitude_list.append(location["Latitude"])

        # Longitude
        longitude_list.append(location["Longitude"])

        # Hour
        hours.append(
            " ".join(
                [
                    str(time["Day"])
                    + ":  "
                    + time["StartTime"]
                    + " to "
                    + time["EndTime"]
                    for time in location["StoreDetailedHours"]
                ]
            )
        )

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
