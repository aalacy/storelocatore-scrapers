import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
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
    base_url = "https://www.unionsavings.com/locations/"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    locations = soup.select("div#locations-wrapper div.item")
    data = []
    for _location in locations:
        location = json.loads(_location["data-info"])
        page_url = location["permalink"]
        location_name = location["name"]
        country_code = "US"
        city = location["city"]
        street_address = location["address"]
        state = location["state"]
        zip = location["zip"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = location["latitude"]
        longitude = location["longitude"]
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        hours_of_operation = soup1.select_one("span.status").text
        phone = "<MISSING>"
        if hours_of_operation != "Closed":
            phone = (
                soup1.select_one(".subcolumn", string=re.compile("Phone"))
                .select("span")[-1]
                .text
            )
            hours = soup1.select_one(
                ".column", string=re.compile("Lobby Hours")
            ).select("span")[1:]
            _hours = []
            for hour in hours:
                _hours.append(": ".join([_ for _ in hour.stripped_strings][::-1]))
            hours_of_operation = "; ".join(_hours)

        _item = [
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

        myutil._check_duplicate_by_loc(data, _item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
