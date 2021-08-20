import csv
import json
import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgselenium import SgChrome

URL = "https://www.games-workshop.com/"


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

    # store data
    locations_ids = []
    locations_titles = []
    street_addresses = []
    cities = []
    store_type_list = []
    states = []
    zip_codes = []
    latitude_list = []
    longitude_list = []
    phone_numbers = []
    hours = []
    countries = []
    stores = []
    links = []

    data = []
    seen = []

    base_links = [
        "https://www.games-workshop.com/en-US/store/fragments/resultsJSON.jsp?latitude=40.2475923&radius=20000&longitude=-77.03341790000002",
        "https://www.games-workshop.com/en-GB/store/fragments/resultsJSON.jsp?latitude=53.2362&radius=500&longitude=-1.42718",
    ]

    driver = SgChrome().driver()
    time.sleep(2)

    for base_link in base_links:
        driver.get(base_link)

        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)

        base = BeautifulSoup(driver.page_source, "lxml")
        stores = json.loads(base.text)["locations"]
        for store in stores:
            if store["type"] == "independentRetailer":
                continue

            # Store ID
            location_id = (
                store["storeId"]
                if "storeId" in store.keys()
                else store["id"].split("-")[-1]
            )

            # Country
            country = store["country"] if "country" in store.keys() else "<MISSING>"
            if country not in ["CA", "US", "GB"]:
                if "county" in store.keys():
                    country = "GB"
                else:
                    continue

            # Name
            location_title = (
                store["name"].strip() if "name" in store.keys() else "<MISSING>"
            )

            # Street
            try:
                street_address = store["address1"] + " " + store["address2"]
            except:
                street_address = store["address1"]

            street_address = (re.sub(" +", " ", street_address)).strip()

            try:
                digit = re.search(r"\d", street_address).start(0)
                if digit != 0:
                    street_address = street_address[digit:]
            except:
                pass

            # State
            state = store["state"] if "state" in store.keys() else "<MISSING>"

            if country == "GB":
                state = store["county"] if "county" in store.keys() else "<MISSING>"

            # city
            city = store["city"] if "city" in store.keys() else "<MISSING>"

            # zip
            zipcode = (
                store["postalCode"].replace(" -", "-").replace("L24R 3N1", "L2R 3N1")
                if "postalCode" in store.keys()
                else "<MISSING>"
            )
            if len(zipcode) == 4:
                zipcode = "0" + zipcode

            if country == "GB" and " " not in zipcode:
                continue

            # store type
            store_type = "<MISSING>"

            # Lat
            lat = store["latitude"] if "latitude" in store.keys() else "<MISSING>"

            # Long
            lon = store["longitude"] if "longitude" in store.keys() else "<MISSING>"
            if lon == -76593137.0:
                lon = -76.593137

            # Phone
            phone = (
                store["telephone"].strip()
                if "telephone" in store.keys()
                else "<MISSING>"
            )
            if phone[:2] == "00":
                phone = phone[2:]
            if len(phone) < 8:
                phone = "<MISSING>"
            # hour
            hour = "<MISSING>"

            link = (
                "https://www.games-workshop.com/en-" + country + "/" + store["seoUrl"]
            )

            # Store data
            locations_ids.append(location_id)
            store_type_list.append(store_type)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zipcode)
            hours.append(hour)
            latitude_list.append(lat)
            longitude_list.append(lon)
            phone_numbers.append(phone)
            cities.append(city)
            countries.append(country)
            links.append(link)

    for (
        link,
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        latitude,
        longitude,
        hour,
        location_id,
        country,
        store_type,
    ) in zip(
        links,
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours,
        locations_ids,
        countries,
        store_type_list,
    ):
        if location_id not in seen:
            data.append(
                [
                    URL,
                    link,
                    locations_title,
                    street_address,
                    city,
                    state,
                    zipcode,
                    country,
                    location_id,
                    phone_number,
                    store_type,
                    latitude,
                    longitude,
                    hour,
                ]
            )
            seen.append(location_id)

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
