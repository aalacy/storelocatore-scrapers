import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("yogasix_com")


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

    base_link = "https://www.yogasix.com/location-search"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.find(class_="location-search__content")["data-locations"]
    stores = json.loads(js)
    for i in stores:
        slug = (
            i.replace("yogasix-", "")
            .replace("westchase-fl", "westchase")
            .replace("san-clemente-ca", "san-clemente")
            .replace("mercer-island-wa", "mercer-island")
        )
        link = "https://www.yogasix.com/location/" + slug

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        try:
            base.find(class_="location-hero hero--coming-soon hero--default").text
            continue
        except:
            pass

        try:
            store_name = base.h1.text.strip()
        except:
            continue
        try:
            hours_js = base.find(
                class_="location-info-map__icon fas fa-clock"
            ).find_next("span")["data-hours"]
            raw_hours = json.loads(hours_js)
            store_opening_hours = ""
            for day in raw_hours:
                store_opening_hours = (
                    store_opening_hours
                    + " "
                    + day.title()
                    + " "
                    + str(raw_hours[day])
                    .replace("], [", " | ")
                    .replace("'", "")
                    .replace(", ", " - ")
                    .replace("[[", "")
                    .replace("]]", "")
                ).strip()
        except:
            store_opening_hours = "<MISSING>"
        if not store_opening_hours:
            store_opening_hours = "<MISSING>"

        try:
            phone_no = (
                base.find(class_="location-info-map__icon fas fa-phone")
                .find_next("div")
                .text.replace("\n", "")
                .strip()
            )
            phone_no = (re.sub(" +", " ", phone_no)).strip()
        except:
            phone_no = "<MISSING>"

        store_address = base.find(class_="location-info-map__info").a.text.strip()
        street_addr = store_address.split("\n")[0].strip()
        state = store_address.split("\n")[1].split(",")[1].split(" ")[-2]
        city = store_address.split("\n")[1].split(",")[0].strip()
        zipcode = store_address.split("\n")[1].split(",")[1].split(" ")[-1]
        coords = (
            base.find(id="map")["data-location"]
            .replace("[", "")
            .replace("]", "")
            .split(",")
        )
        lon = coords[0].strip()
        lat = coords[1].strip()

        yield [
            "https://www.yogasix.com/",
            link,
            store_name,
            street_addr,
            city,
            state,
            zipcode,
            "US",
            "<MISSING>",
            phone_no,
            "<MISSING>",
            lat,
            lon,
            store_opening_hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
