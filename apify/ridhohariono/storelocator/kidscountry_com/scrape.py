import csv
from sgselenium import SgSelenium


DOMAIN = "kidscountry.com"
BASE_URL = "https://www.kidscountry.com"
LOCATION_URL = "https://www.kidscountry.com/find-a-school"


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
    contents = driver.find_elements_by_css_selector(
        "div[data-testid='gallery-item-item']"
    )
    all_store_data = []
    for row in contents:
        location_name = row.find_element_by_css_selector(
            "div[data-testid='gallery-item-title']"
        ).text.strip()
        info = (
            row.find_element_by_css_selector(
                "p[data-testid='gallery-item-description']"
            )
            .text.strip()
            .split("\n")
        )
        address = info[0].split(",")
        street_address = address[0].strip()
        city = address[1].strip()
        state = address[2].split(" ")[1]
        zip_code = address[2].split(" ")[2]
        print(address[2].split(" "))
        phone = info[-1].strip()
        hours_of_operation = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        page_url = LOCATION_URL
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
