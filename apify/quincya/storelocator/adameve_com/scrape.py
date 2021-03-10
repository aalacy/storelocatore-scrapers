import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

log = SgLogSetup().get_logger("adameve.com")


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

    base_link = "https://www.adameve.com/store"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found = []

    items = base.find_all(class_="row cardStores")
    locator_domain = "adameve.com"

    for item in items:
        link = "https://www.adameve.com" + item.a["href"]

        if "united-states" in link:
            country_code = "US"
        elif "canada" in link:
            country_code = "CA"
        else:
            continue

        if link in found:
            continue

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "Your Session Was Rejected" in base.text:
            base = item
            raw_address = list(
                base.find(class_="column store-card-address").stripped_strings
            )
            street_address = raw_address[0].strip()
            city_line = raw_address[1].split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            phone = raw_address[-1].strip()
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            link = base_link
            location_name = "ADAM & EVE " + city

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
        else:
            bases = base.find_all(class_="row cardStores")
            found.append(link)
            log.info(link)

            location_name = base.h1.get_text(" ").strip()

            for base in bases:
                raw_address = list(base.find(class_="address").stripped_strings)
                street_address = raw_address[0].strip()
                city_line = raw_address[1].split(",")
                city = city_line[0].strip()
                state = city_line[1].strip()
                zip_code = city_line[2].strip()
                store_number = base.find(class_="btn-group-sm").a["elementtag-1"]
                location_type = "<MISSING>"
                phone = raw_address[-1].strip()
                hours_of_operation = " ".join(
                    list(base.find(class_="storesHours").stripped_strings)
                )

                map_link = base.find(class_="btn-group-sm").a["href"]
                req = session.get(map_link, headers=headers)
                maps = BeautifulSoup(req.text, "lxml")

                try:
                    raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                    latitude = raw_gps[
                        raw_gps.find("=") + 1 : raw_gps.find("%")
                    ].strip()
                    longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()

                    if not longitude:
                        geo = re.findall(
                            r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", raw_gps
                        )[0].split(",")
                        latitude = geo[0]
                        longitude = geo[1]
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

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
