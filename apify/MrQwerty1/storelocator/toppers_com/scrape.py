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
    locator_domain = "https://toppers.com/"
    api_url = "https://toppers.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations')]/text()"))
    text = (
        text.split("var locations = ")[1].split("var mapPinContentUrl")[0].strip()[:-1]
    )
    js = json.loads(text)

    for j in js:
        street_address = (
            f"{j.get('Line1')} {j.get('Line2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("StateAbbreviation") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("LocationId") or "<MISSING>"
        page_url = f'https://toppers.com/locations/{city.lower().replace(" ", "-")}'
        location_name = j.get("StoreName")
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        text = j.get("HoursJson") or "{}"
        hours = json.loads(text)

        for h in hours:
            t = h.get("Type")
            if t != 0:
                continue

            index = h.get("DayOfWeek")
            if not index:
                continue

            day = days[index]
            start = h.get("OpenTime")
            close = h.get("CloseTime")

            _tmp.append(f"{day}: {start} - {close}")

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
