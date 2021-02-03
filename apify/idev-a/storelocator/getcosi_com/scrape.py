import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
import json
import re

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


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
    base_url = "https://www.getcosi.com/locations/"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    locations = json.loads(
        soup.find("script", string=re.compile("locations"))
        .string.split("locations: ")[1]
        .split("apiKey: ")[0]
        .strip()[:-1]
    )
    data = []
    for location in locations:
        page_url = urljoin("https://www.getcosi.com", location["url"])
        location_name = location["name"]
        country_code = "US"
        city = location["city"]
        street_address = location["street"]
        state = location["state"]
        zip = location["postal_code"]
        phone = location["phone_number"]
        store_number = location["id"]
        location_type = "<MISSING>"
        latitude = location["lat"]
        longitude = location["lng"]
        tags = bs(location["hours"], "lxml")
        hours_of_operation = (
            "; ".join(
                [
                    _.text
                    for _ in tags.select("p")
                    if not _.find("a") and "This location" not in _.text
                ]
            )
            or "<MISSING>"
        )

        _hours = re.findall(r"\w+:;", hours_of_operation)
        for hour in _hours:
            hours_of_operation = hours_of_operation.replace(hour, hour[:-1])

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
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


if __name__ == "__main__":
    scrape()
