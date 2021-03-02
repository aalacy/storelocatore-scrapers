import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("lemacaron-us_com")


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

    base_link = "https://lemacaron-us.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="location-links")
    locator_domain = "lemacaron-us.com"

    lats = []
    for item in items:

        link = "https://lemacaron-us.com" + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if (
            "COMING SOON" in base.h2.text.upper()
            or "COMING SOON" in base.find(class_="text-fade px-2 mb-2").text.upper()
        ):
            continue

        logger.info(link)

        location_name = base.h2.span.text

        raw_address = base.find(class_="text-fade px-2 mb-2").text.strip().split("\n")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip().split(",")[0].strip()

        try:
            state = raw_address[1].strip().split(",")[1].strip().split()[0]
        except:
            continue
        zip_code = raw_address[1].strip().split(",")[1].strip().split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = base.find_all(class_="btn btn-sm btn-primary btn-icon")[-3].text
        if "coming" in phone.lower():
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = base.find_all(class_="btn btn-sm btn-primary btn-icon")[-1]["href"]
        if "maps" in map_link:
            req = session.get(map_link, headers=headers)
            maps = BeautifulSoup(req.text, "lxml")

            try:
                raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
                longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
                if len(latitude) < 5 or latitude + longitude in lats:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                else:
                    lats.append(latitude + longitude)
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        hours_of_operation = (
            base.find(class_="text-fade px-2 mb-3").text.replace("\r\n", " ").strip()
        )
        if not hours_of_operation:
            try:
                hours_raw = (
                    base.find(class_="text-fade px-2 mb-3")
                    .next_element.text.replace("\r\n", " ")
                    .strip()
                )
                if "am" in hours_raw.lower() or "pm" in hours_raw.lower():
                    hours_of_operation = hours_raw
            except:
                pass
        if not hours_of_operation:
            rows = list(base.address.stripped_strings)
            for row in rows:
                if "day-" in row:
                    hours_of_operation = hours_of_operation + " " + row

        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        if "(" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("(")
            ].strip()
        if not hours_of_operation or "click" in hours_of_operation.lower():
            hours_of_operation = "<MISSING>"

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
