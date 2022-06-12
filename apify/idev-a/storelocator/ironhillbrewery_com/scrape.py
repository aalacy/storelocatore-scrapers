import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


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


def _headers():
    return {
        "accept": "application/xml, text/xml, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }


def fetch_data():
    data = []

    locator_domain = "https://ironhillbrewery.com/"
    r = session.get(locator_domain, headers=_headers())
    soup = bs(r.text.strip(), "lxml")
    links = soup.select_one("#nav--main li.has-submenu").select("ul li a")
    for link in links[1:-1]:
        page_url = link["href"]
        r1 = session.get(page_url, headers=_headers())
        soup = bs(r1.text.strip(), "lxml")
        location = json.loads(
            soup.find("script", type="application/ld+json").string.strip()
        )
        location_name = location["name"]
        store_number = "<MISSING>"
        street_address = location["address"]["streetAddress"]
        city = location["address"]["addressLocality"]
        state = location["address"]["addressRegion"]
        zip = location["address"]["postalCode"]
        country_code = "US"
        phone = myutil._valid(location.get("telephone"))
        location_type = location["@type"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = myutil._valid("; ".join(location["openingHours"]))

        _item = [
            locator_domain,
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

        data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
