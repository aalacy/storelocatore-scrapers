import re
import csv
import json
from urllib.parse import unquote
from w3lib.html import remove_tags

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://waldensavings.bank/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall("llocdata =(.+);", response.text)[0]

    all_locations = json.loads(data)
    for poi in all_locations:
        store_url = start_url
        location_name = poi["locName"]
        raw_address = (
            unquote(poi["AddressNoHtml"])
            .replace("\n", " ")
            .replace("\r", "")
            .split("Phone:")[0]
            .strip()
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "<MISSING>"
        store_number = poi["LocationId"]
        phone = (
            unquote(poi["AddressNoHtml"])
            .replace("\n", " ")
            .replace("\r", "")
            .split("Phone:")[-1]
            .split("Fax:")[0]
            .strip()
        )
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        longitude = poi["Longitude"]
        hoo = (
            remove_tags(unquote(poi["Hours"]))
            .replace("&nbsp;", " ")
            .replace("\r\n", " ")
        )
        if not hoo:
            hoo = (
                remove_tags(unquote(poi["Lobby"]))
                .replace("&nbsp;", " ")
                .replace("\r\n", " ")
            )
        hours_of_operation = hoo if hoo else "<MISSING>"

        item = [
            domain,
            store_url,
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
