import csv
import json
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

    locator_domain = "https://shopqualityfoods.com"
    page_url = "https://shopqualityfoods.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "jQuery(document).ready(function($)")]/text()'
            )
        )
        .split('"places":')[1]
        .split(',"listing":')[0]
    )
    js = json.loads(jsblock)
    for j in js:

        location_name = j.get("title")
        location_type = "<MISSING>"
        street_address = "".join(j.get("content")).split("<")[0].strip()
        a = j.get("location")
        phone = "".join(j.get("content")).split("Phone:")[1].split("<")[0].strip()
        state = a.get("state")
        postal = a.get("postal_code") or "<MISSING>"
        country_code = "US"
        city = a.get("city")
        store_number = "<MISSING>"
        latitude = a.get("lat")
        longitude = a.get("lng")
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
