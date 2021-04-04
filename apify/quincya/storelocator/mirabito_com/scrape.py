import csv
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://www.mirabito.com/convenience-stores/locations/"

    driver = SgChrome().chrome()
    time.sleep(2)

    driver.get(base_link)
    time.sleep(2)

    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located((By.CLASS_NAME, "wpgmaps_mlist_row"))
    )
    time.sleep(2)

    base = BeautifulSoup(driver.page_source, "lxml")

    data = []

    items = base.find_all(class_="wpgmaps_mlist_row")
    locator_domain = "mirabito.com"

    for item in items:

        location_name = item.a.text.strip()

        raw_address = (
            item["data-address"]
            .replace("17, RD", "17 RD")
            .replace("Street, Rte", "Street Rte")
            .replace("232, Watertown", "232 Watertown")
            .replace("Street, Adams", "Street Adams")
            .replace(", USA", "")
            .split(",")
        )

        if len(location_name.split("-")) == 2:
            city = location_name.split("-")[-1].strip()
        else:
            city = location_name.split("-")[-2].strip()

        street_address = (
            raw_address[0][: raw_address[0].rfind(city)].replace("Norwic", "").strip()
        )
        state = raw_address[1].strip()[:-6].strip()
        zip_code = raw_address[-1][-6:].strip()

        if zip_code == "NY":
            state = "NY"
        if street_address == "32 East Church Street":
            zip_code = "13605"

        country_code = "US"
        store_number = item.find(
            "p", attrs={"data-custom-field-name": "Store Number"}
        ).text.strip()

        location_type = ""
        raw_types = item.find(class_="wpgmza_custom_fields").find_all("p")[9:]
        for raw_type in raw_types:
            location_type = location_type + ", " + raw_type["data-custom-field-name"]
        location_type = location_type[1:].strip()
        phone = item.find(
            "p", attrs={"data-custom-field-name": "Phone Number"}
        ).text.strip()

        hours_of_operation = ""
        raw_hours = item.find(class_="wpgmza_custom_fields").find_all("p")[:7]
        for raw_hour in raw_hours:
            hours_of_operation = (
                hours_of_operation
                + " "
                + raw_hour["data-custom-field-name"]
                + " "
                + raw_hour.text.strip()
            ).strip()

        latitude = item["data-latlng"].split(",")[0].strip()
        longitude = item["data-latlng"].split(",")[1].strip()

        data.append(
            [
                locator_domain,
                base_link,
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
        )
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
