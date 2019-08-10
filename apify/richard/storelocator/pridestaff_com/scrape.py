import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


COMPANY_URL = "https://www.pridestaff.com"
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
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
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
        "nav.site-nav > ul.ml-0.mb-0 > li:nth-child(3) > a"
    )[0].get_attribute("href")
    driver.get(store_url)

    # Get all locations url
    listing_urls = [
        listing_url.get_attribute("href")
        for listing_url in driver.find_elements_by_css_selector(
            "div.row.row-cell--third.locations > div > ul.noaftermath > li > a"
        )
    ]

    for listing_url in listing_urls:
        driver.get(listing_url)

        # Wait until element appears - 10 secs max
        wait = WebDriverWait(driver, 10)
        wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "h2.center")))

        # Extract location information
        location_title = driver.find_element_by_class_name("h2.center").text
        address_info = [
            location_info.text
            for location_info in driver.find_elements_by_css_selector(
                "ul.location-address.noaftermath > li"
            )
        ]
        if address_info[0] == "Coming Soon":
            street_address = "<MISSING>"
        else:
            street_address = " ".join(address_info[:-1])
        city = address_info[-1].split(",")[0]
        state = address_info[-1].split(",")[1].split(" ")[0]
        zip_code = address_info[-1].split(",")[1].split(" ")[1]
        try:
            phone_number = driver.find_element_by_css_selector(
                "ul.location-contact > li:nth-child(1) > a"
            ).text
        except:
            phone_number = "<MISSING>"

        # Store information
        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        phone_numbers.append(phone_number)
        countries.append("US")

    for (
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        country,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        countries,
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
                "<MISSING>",
                phone_number,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
