import csv
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgselenium import SgChrome


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

    base_link = "https://www.tillys.com/store-list/"

    driver = SgChrome().chrome()
    time.sleep(2)

    driver.get(base_link)
    WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.ID, "primary")))
    time.sleep(2)

    base = BeautifulSoup(driver.page_source, "lxml")

    data = []
    locator_domain = "tillys.com"

    stores = base.find_all(class_="col-6 col-sm-3 sl__stores-list_item")

    for i, store in enumerate(stores):
        location_name = store.find(class_="sl__stores-list_name-link").text.strip()

        if "coming soon" in location_name.lower():
            continue

        link = (
            "https://www.tillys.com"
            + store.find(class_="sl__stores-list_name-link")["href"]
        )

        raw_address = list(
            store.find("div", attrs={"itemprop": "address"}).stripped_strings
        )

        try:
            phone = store.find("div", attrs={"itemprop": "telephone"}).text.strip()
        except:
            phone = "<MISSING>"

        if len(raw_address) == 3 and phone != "<MISSING>":
            street_address = raw_address[0].strip()
            city = raw_address[1].split(",")[0].strip()
            state = raw_address[1].split(",")[1].strip().split("\n")[0]
            zip_code = raw_address[1].split(",")[1].strip().split("\n")[1]
        if len(raw_address) == 4 or phone == "<MISSING>":
            street_address = raw_address[0].strip() + " " + raw_address[1].strip()
            city = raw_address[2].split(",")[0].strip()
            state = raw_address[2].split(",")[1].strip().split("\n")[0]
            zip_code = raw_address[2].split(",")[1].strip().split("\n")[1]

        country_code = "US"
        store_number = link.split("=")[-1]
        if not store_number.isnumeric():
            store_number = "<MISSING>"
        location_type = "<MISSING>"

        if "temporarily closed" in str(store).lower():
            hours_of_operation = "Temporarily Closed"
        else:
            days = list(store.time.stripped_strings)[:7]
            hours = list(store.time.stripped_strings)[7:]
            hours_of_operation = ""
            for i in range(len(days)):
                hours_of_operation = (
                    hours_of_operation + " " + days[i] + " " + hours[i]
                ).strip()

        geo = (
            store.find("a", string="Driving directions")["href"]
            .split("//")[-1]
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]

        data.append(
            [
                locator_domain,
                link,
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
