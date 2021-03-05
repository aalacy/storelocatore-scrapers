import csv
import re

from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://extremebodyshaping.com/"
    api_url = "https://extremebodyshaping.com/Locations-Map"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = (
        "".join(tree.xpath("//script[contains(text(), 'detailLocations =')]/text()"))
        .split("detailLocations =")[1]
        .split("];")[0]
        .strip()[:-1]
        + "]"
    )
    text = re.sub(r"(\w+(?<!https)):", r'"\1":', text)
    js = eval(text)

    for j in js:
        street_address = j.get("sA") or "<MISSING>"
        city = j.get("aL") or "<MISSING>"
        state = j.get("aR") or "<MISSING>"
        postal = j.get("pC") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
