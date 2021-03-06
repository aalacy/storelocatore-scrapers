import csv
import re
from sgselenium import SgSelenium


DOMAIN = "classiccleaners.com"
BASE_URL = "https://classiccleaners.com"
LOCATION_URL = "https://classiccleaners.net/locations-delivery/locations-carmel-fishers-indianapolis-oaklandon-geist-broadripple-fortville/locations/"


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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def get_text(element, query):
    return (
        element.find_element_by_css_selector(query)
        .get_attribute("innerHTML")
        .replace(u"\u200e", "")
    )


def fetch_data():
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    main = driver.find_element_by_css_selector("div#map_sidebar")
    all_stores = main.find_elements_by_css_selector("div.results_wrapper")
    all_store_data = []
    for row in all_stores:
        location_name = get_text(row, "span.location_name").strip()
        street_address = (
            get_text(row, "span.slp_result_street")
            + " "
            + get_text(row, "span.slp_result_street2")
        )
        city_state_zip = get_text(row, "span.slp_result_citystatezip")
        city = city_state_zip.split(",")[0].strip()
        state = (
            "IN"
            if "Indiana" in city_state_zip.split(" ")[1].strip()
            else city_state_zip.split(" ")[1].strip()
        )
        zip_code = city_state_zip.split(" ")[2].strip()
        phone = handle_missing(
            re.sub(r", For Home.*", "", get_text(row, "span.slp_result_phone"))
        )
        hoo = get_text(row, "span.slp_result_hours").strip()
        hoo = re.sub(r"Express.*", "", hoo).replace("\n", "")
        hoo = re.sub(r"Drive.*", "", hoo)
        hoo = re.sub(r"24.*", "", hoo).replace("Closed Sunday", "Sunday: Closed")
        hours_of_operation = handle_missing(re.sub(r",$.*", "", hoo.strip()))
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
