import csv
from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json


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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def get_json_data(html):
    re_get_json = r"var location_data[\s\S]*?=[\s\S]*?(.+?);$"
    match = re.search(re_get_json, html, re.MULTILINE)
    json_text = match.group(1)
    return json.loads(json_text)


driver = SgSelenium().chrome()


def fetch_data():

    all = []
    driver.get("https://parisbaguette.com/locations/")

    iframe = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "locator_iframe10764"))
    )
    driver.switch_to.frame(iframe)
    json_stores = get_json_data(driver.page_source)

    for store in json_stores:

        loc = store["name"]
        if "coming soon" in loc.lower():
            continue
        street = store["address"]
        city = store["city"]
        state = store["state"]
        zc = store["postalcode"] if "postalcode" in store else "<MISSING>"
        try:
            phone = store["phone"]
        except:
            phone = "<MISSING>"
        store_num = store["id"]
        lat = store["lat"]
        lng = store["lng"]
        hours = store["storehours1"] if "storehours1" in store else "<MISSING>"
        hours = (
            hours + (", " + store["storehours2"])
            if "storehours2" in store
            else "<MISSING>"
        )

        all.append(
            [
                "https://parisbaguette.com/",
                loc,
                street,
                city,
                state,
                zc,
                "US",
                store_num,
                phone,  # phone
                "<MISSING>",  # type
                lat,
                lng,
                hours,  # timing
                "https://parisbaguette.com/locations/",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
