import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.adameve.com"
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
    hours = []
    countries = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Fetch stores
    location_url = "https://www.adameve.com/store"
    driver.get(location_url)

    while True:
        if (
            len(driver.find_elements_by_css_selector("div.btn-index-container > a"))
            != 0
        ):
            store_urls = [
                url.get_attribute("href")
                for url in driver.find_elements_by_css_selector(
                    "div.btn-index-container > a"
                )
            ]
            break

    for store_url in store_urls:
        if "united-states" in store_url or "canada" in store_url:
            driver.get(store_url)

            locations_titles.append(
                driver.find_element_by_css_selector("h1.titlePage").get_attribute(
                    "textContent"
                )
            )
            street_addresses.append(
                driver.find_element_by_css_selector(
                    "figcaption.spacer:nth-of-type(1)"
                ).text
            )
            cities.append(
                driver.find_element_by_css_selector("figcaption.spacer:nth-of-type(2)")
                .text.split(",")[0]
                .strip()
            )
            states.append(
                driver.find_element_by_css_selector("figcaption.spacer:nth-of-type(2)")
                .text.split(",")[1]
                .strip()
            )
            zip_codes.append(
                driver.find_element_by_css_selector("figcaption.spacer:nth-of-type(2)")
                .text.split(",")[2]
                .strip()
            )
            phone_numbers.append(
                driver.find_element_by_css_selector(
                    "figcaption.spacer:nth-of-type(3)"
                ).text
            )
            hours.append(
                driver.find_element_by_css_selector(
                    "table.storesHours > tbody"
                ).get_attribute("textContent")
            )

            if "united-states" in store_url:
                countries.append("US")
            else:
                countries.append("CA")

    # Store data
    for (
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        hour,
        country,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        hours,
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
                hour,
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
