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


def get_hoo(url):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    script = "".join(
        tree.xpath("//script[contains(text(), 'http://schema.org/')]/text()")
    ).strip()
    js = json.loads(script)

    _tmp = []
    i = 0
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hours = js.get("openingHours")
    for h in hours:
        day = days[i]
        time = h[2:].strip()
        if not time:
            time = "Closed"
        _tmp.append(f"{day}: {time}")
        i += 1

    return ";".join(_tmp)


def fetch_data():
    out = []
    locator_domain = "https://www.tileshop.com/"
    api_url = "https://www.tileshop.com/api/Stores/SearchByCoordinates?lat=44.98&lng=-93.45&distance=8000&take=5000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        location_name = j.get("StoreName")
        street_address = (
            f"{j.get('AddressLine1')} {j.get('AddressLine2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("StateCode") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("StoreNumber") or "<MISSING>"
        page_url = f'https://www.tileshop.com/store-locator/{j.get("Name")}'
        phone = j.get("Phone1") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for d in days:
            _tmp.append(f'{d}: {j.get(f"{d}Hours")}')

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.find("None") != -1:
            hours_of_operation = get_hoo(page_url)

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
