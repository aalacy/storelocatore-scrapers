# -*- coding: utf-8 -*-
import csv
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

        location_name = base.h1.text.strip()
        raw_address = list(base.find(class_="it-prop-details-group").p.stripped_strings)
        street_address = raw_address[0].split(" , (")[0].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = (
            base.find_all(class_="it-prop-details-group")[1]
            .text.replace("Reservations", "")
            .replace("(Spanish or English)", "")
            .strip()
        )
        try:
            hours_of_operation = (
                base.find(class_="it-prop-details-group-hours-inner")
                .text.replace("\n", " ")
                .strip()
            )
            if "Please" in hours_of_operation:
                hours_of_operation = hours_of_operation[
                    : hours_of_operation.find("Please")
                ].strip()
        except:
            hours_of_operation = "<MISSING>"

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        map_str = base.find(id="directions_box").a["href"]
        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(",")
        latitude = geo[0]
        longitude = geo[1]

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
