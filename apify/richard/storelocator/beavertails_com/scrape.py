import csv
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://beavertails.com"
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
    street_addresses = []
    store_ids = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    hours = []
    longitude_list = []
    latitude_list = []
    countries = []
    data = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = driver.find_elements_by_css_selector(
        "ul.fullwidth-menu.nav.upwards > li:nth-child(4) > a"
    )[0].get_attribute("href")
    driver.get(store_url)

    # Loading
    time.sleep(2)

    # Get all listings
    listings = driver.find_elements_by_css_selector("div.wpsl-store-location")

    for listing in listings:
        location_title = listing.find_element_by_css_selector("p > strong").text
        street_address = " ".join(
            [
                address.text
                for address in listing.find_elements_by_css_selector(
                    "p > span.wpsl-street"
                )
            ]
        )
        country = listing.find_element_by_css_selector("p > span.wpsl-country").text
        city_state_info = listing.find_element_by_css_selector(
            "p > span:not(.wpsl-country):not(.wpsl-street)"
        ).text

        if country == "Canada":
            zip_code = city_state_info[-7:]
        else:
            zip_code = city_state_info[-5:]

        # Hours not always present
        try:
            hour = listing.find_element_by_css_selector("table.wpsl-opening-hours").text
        except:
            hour = "<MISSING>"

        locations_titles.append(location_title)
        street_addresses.append(street_address)
        zip_codes.append(zip_code)
        hours.append(hour)
        countries.append(country)

    # Get other information
    driver.get(
        "https://beavertails.com/wp-admin/admin-ajax.php?lang=en&action=store_search&lat=45.501689&lng=-73.56725599999999&max_results=500&search_radius=50000&filter=43"
    )
    listings = json.loads(driver.find_element_by_css_selector("pre").text)
    for listing in listings:
        store_ids.append(listing["id"])
        cities.append(listing["city"])
        states.append(listing["state"])
        latitude_list.append(listing["lat"])
        longitude_list.append(listing["lng"])
        zip_codes.append(listing["zip"])
        if listing["phone"] == "":
            phone_numbers.append("<MISSING>")
        else:
            phone_numbers.append(listing["phone"])

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
        country,
        store_number,
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
        countries,
        store_ids,
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
                store_number,
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
