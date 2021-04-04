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
    locator_domain = "https://www.payomatic.com/"
    api_url = "https://www.payomatic.com/store-locator/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    script = "".join(tree.xpath("//script[contains(text(), 'var stores_data')]/text()"))
    line = ""
    for s in script.split("\n"):
        if s.find("var stores_data") != -1:
            line = s.split("var stores_data =")[1][:-1]

    js = json.loads(line)["features"]

    for j in js:
        geo = j.get("geometry", {}).get("coordinates") or ["<MISSING>", "<MISSING>"]
        j = j["properties"]
        location_name = j.get("location_name")
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("store_code") or "<MISSING>"
        page_url = j.get("permalink") or "<MISSING>"
        phone = j.get("primary_phone") or "<MISSING>"
        latitude = geo[1] or "<MISSING>"
        longitude = geo[0] or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("store_hours") or {}
        for k, v in hours.items():
            _tmp.append(f"{k.capitalize()}: {v}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
