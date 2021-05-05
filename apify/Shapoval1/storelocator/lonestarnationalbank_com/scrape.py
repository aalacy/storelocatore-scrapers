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
    locator_domain = "https://www.lonestarnationalbank.com/locations/"
    api_url = "https://www.lonestarnationalbank.com/a80ffd210dffea6c5cfb9968d6f0a5b18f5d9718-9663d157b5abb14b3eef.js"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath("//*//text()"))
        .split("parse('")[1]
        .split("')}}]);")[0]
        .replace("\\", "")
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:

        phone = j.get("phone") or "<MISSING>"
        street_address = j.get("streetAddress")
        city = j.get("city")
        state = j.get("state")
        location_name = j.get("name")
        country_code = "US"
        store_number = "<MISSING>"
        latitude = j.get("geo")[1]
        longitude = j.get("geo")[0]
        location_type = j.get("category") or "<MISSING>"
        hours = j.get("lobbyHours") or "<MISSING>"
        tmp = []
        if hours != "<MISSING>":
            for h in hours:
                day = h.get("days")
                times = h.get("times")
                line = f"{day} {times}"
                tmp.append(line)

        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if location_type == "ATM":
            hours_of_operation = "24 hrs"
        postal = j.get("zipCode")
        page_url = "https://www.lonestarnationalbank.com/locations/"

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
