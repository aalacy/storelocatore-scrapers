import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("mtb_com")


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
    base_link = "https://locations.mtb.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "mtb.com"

    state_links = []
    states = base.find(id="map-container").find_all(class_="mapListItem")
    for state in states:
        state_links.append(state.a["href"])

    city_links = []
    for state_link in state_links:
        logger.info(state_link)
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        cities = base.find_all(class_="mapListItem")
        for city in cities:
            city_link = city.a["href"]
            if city_link not in city_links:
                city_links.append(city_link)

    logger.info("Processing " + str(len(city_links)) + " links ..")
    for city_link in city_links:
        req = session.get(city_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find(class_="map-list").find_all(class_="mapListItem")

        for item in items:
            location_type = item.find(class_="locationType").text.strip()
            link = item.a["href"]
            location_name = item.find(class_="locationName").a.text.strip()
            street_address = item.find(class_="addr").text.strip()
            city_line = item.find(class_="csz").text.strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            phone = item.find(class_="phone mt-10").text.strip()
            if not phone:
                phone = "<MISSING>"
            store_number = link.split("-")[-1].split(".")[0]

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            street_address = base.find("meta", attrs={"property": "og:street-address"})[
                "content"
            ]

            if "13 & 896" not in street_address and "Route" not in street_address:
                try:
                    digit = re.search(r"\d", street_address).start(0)
                    if digit != 0:
                        street_address = street_address[digit:]
                except:
                    pass

            hours_of_operation = parse_hours(base)

            latitude = base.find("meta", attrs={"property": "og:latitude"})["content"]
            longitude = base.find("meta", attrs={"property": "og:longitude"})["content"]

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


def parse_hours(base):
    hours_of_operation = "<MISSING>"

    if base.find(id="primary-hours") and base.find(id="primary-hours").find(
        class_="hours"
    ):
        hours_of_operation = (
            " ".join(
                list(
                    base.find(id="primary-hours").find(class_="hours").stripped_strings
                )
            )
            .replace("Holiday Hours", "")
            .replace("  ", " ")
        )
    elif base.find(class_="hours") and base.find(class_="hours").find(class_="hours"):
        hours_of_operation = (
            " ".join(
                list(base.find(class_="hours").find(class_="hours").stripped_strings)
            )
            .replace("Holiday Hours", "")
            .replace("  ", " ")
        )

    if (
        hours_of_operation
        == "Mon Closed Tue Closed Wed Closed Thu Closed Fri Closed Sat Closed Sun Closed"
    ):
        hours_of_operation = "Temporarily Closed"
    return hours_of_operation


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
