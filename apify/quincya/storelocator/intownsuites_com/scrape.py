# -*- coding: utf-8 -*-
import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("intownsuites_com")


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

    base_link = "https://www.intownsuites.com/extended-stay-locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found_poi = []
    all_links = []
    items = base.find(id="locationsList").find_all("li")
    locator_domain = "intownsuites.com"

    logger.info("Finding links ..")
    for item in items:
        link = item.a["href"]
        if link[:2] == "//":
            link = "https:" + link
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        new_items = base.find_all(
            "div", attrs={"data-pagetmp": "extended-stay-locations"}
        )
        for new_item in new_items:
            link = new_item.a["href"]
            if link not in all_links:
                all_links.append(link)
        if not new_items:
            if link not in all_links:
                all_links.append(link)

    logger.info("Processing %s links .." % (len(all_links)))
    for link in all_links:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        all_scripts = base.find_all("script", attrs={"type": "application/ld+json"})
        for script in all_scripts:
            if "longitude" in str(script):
                fin_script = (
                    script.text.replace("\n", "")
                    .replace("\r", "")
                    .replace("Shipt Grocery Delivery}", 'Shipt Grocery Delivery"}')
                    .strip()
                )

        store = json.loads(fin_script)
        location_name = store["name"].replace("&#8211;", "-").replace("–", "-").strip()
        if (
            link
            == "https://www.intownsuites.com/extended-stay-locations/south-carolina/charleston/savannah-highway/"
        ):
            location_name = "InTown Suites Extended Stay Charleston SC - Savannah Hwy"
        street_address = (
            store["address"]["streetAddress"].replace("&nbsp;", " ").strip()
        )
        street_address = (re.sub(" +", " ", street_address)).strip()
        try:
            city = store["address"]["addressLocality"]
        except:
            pass
        state = store["address"]["addressRegion"]
        try:
            zip_code = store["address"]["postalCode"]
        except:
            zip_code = store["address"]["postOfficeBoxNumber"]
        if street_address == "6451 Bandera Road":
            city = "Leon Valley"
            state = "TX"
            zip_code = "78238"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = (
            base.find(class_="css_table_cell address")
            .p.text.replace("Reservations:", "")
            .replace("(Spanish or English)", "")
            .strip()
        )
        try:
            hours_of_operation = (
                base.find(class_="css_table_cell office_hours")
                .find_all("p")[-1]
                .text.replace("\n", " ")
                .strip()
            )
            if "Please" in hours_of_operation:
                hours_of_operation = hours_of_operation[
                    : hours_of_operation.find("Please")
                ].strip()
        except:
            hours_of_operation = "<MISSING>"

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"].replace(",", "")
        if latitude == longitude:
            map_link = base.find(class_="container ft_map_and_directions").a["href"]
            longitude = map_link[map_link.find("-") : map_link.find("&")].replace(
                ",", ""
            )
        if location_name == "InTown Suites Extended Stay Atlanta GA - Sandy Springs":
            latitude = "33.918987"
            longitude = "-84.375590"

        if location_name not in found_poi:
            found_poi.append(location_name)
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
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
