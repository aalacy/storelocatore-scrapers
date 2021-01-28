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
    locator_domain = "https://www.affordabledentures.com/"
    api_url = "https://www.affordabledentures.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'window.Launchpad.Map.Locations =')]/text()"
        )
    )
    text = text.split("window.Launchpad.Map.Locations =")[-1].strip()[:-1]
    js = json.loads(text)

    for j in js:
        a = j.get("Address")
        street_address = (
            f'{a.get("Address1")} {a.get("Address2") or ""}'.strip() or "<MISSING>"
        )
        city = a.get("City") or "<MISSING>"
        state = a.get("State", {}).get("Abbreviation") or "<MISSING>"
        postal = a.get("Zipcode") or "<MISSING>"
        if len(postal) == 4:
            postal = f"0{postal}"
        country_code = "US"
        store_number = j.get("PracticeId") or "<MISSING>"
        page_url = f'https://www.affordabledentures.com{j.get("Url")}'
        location_name = j.get("Title") or "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
        latitude = a.get("Latitude") or "<MISSING>"
        longitude = a.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("Hours", {}) or {}
        for k, v in hours.items():
            start = v.get("From")
            close = v.get("To")
            if start:
                _tmp.append(f"{k.capitalize()}: {start} - {close}")
            else:
                _tmp.append(f"{k.capitalize()}: Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

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
