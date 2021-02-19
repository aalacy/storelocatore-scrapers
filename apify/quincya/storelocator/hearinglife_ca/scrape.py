import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="hearinglife.ca")


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

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.hearinglife.ca/Centers"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "hearinglife.ca"

    data = []

    items = base.find_all(class_="center-list-item")

    log.info("Processing " + str(len(items)) + " links ..")
    for item in items:

        link = "https://www.hearinglife.ca" + item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = " ".join(
            list(base.find(class_="hours-list").stripped_strings)
        )
        script = (
            base.find("script", attrs={"type": "application/ld+json"})
            .text.replace("\n", "")
            .strip()
        )
        store = json.loads(script)

        street_address = store["address"]["streetAddress"]
        try:
            digit = re.search(r"\d", street_address).start(0)
            if digit != 0:
                street_address = street_address[digit:]
        except:
            pass

        location_name = store["name"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        phone = store["telephone"]
        country_code = "CA"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

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
