import csv
import json
from sgselenium import SgSelenium


DOMAIN = "worldwidegolfshops.com"
BASE_URL = "https://www.worldwidegolfshops.com/uinta-golf"
LOCATION_URL = "https://www.worldwidegolfshops.com/uinta-golf/"


def addy_ext(addy):
    addy = addy.split(",")
    city = addy[0]
    state_zip = addy[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
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
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)

    hrefs = driver.find_elements_by_xpath("//a[contains(@class, 'store-name-link')]")
    link_list = []
    for h in hrefs:
        link_list.append(h.get_attribute("href"))
    link_list = list(dict.fromkeys(link_list))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        main = driver.find_element_by_css_selector(
            "script[type='application/ld+json']"
        ).get_attribute("innerHTML")
        data = json.loads(main)
        location_name = driver.find_element_by_css_selector(
            "h1.vtex-yext-store-locator-0-x-storeTitle"
        ).text.strip()

        street_address = data["address"]["streetAddress"]
        city = data["address"]["addressLocality"]
        state = data["address"]["addressRegion"]
        zip_code = data["address"]["postalCode"]
        phone = data["telephone"]
        hours_of_operation = (
            driver.find_element_by_css_selector(
                "div.vtex-yext-store-locator-0-x-normalHours"
            )
            .text.replace("\n", " ")
            .replace("STORE HOURS ", "")
        )
        store_number = data["@id"]
        location_type = "<MISSING>"
        latitude = data["geo"]["latitude"]
        longitude = data["geo"]["longitude"]
        page_url = link
        country_code = "US"

        store_data = [
            DOMAIN,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
