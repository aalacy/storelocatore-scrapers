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


def get_hours(url):
    _tmp = []
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@class='structured-data-widget']/text()"))
    text = (
        text.split('"openingHoursSpecification":')[1].split('"hasMap"')[0].strip()[:-1]
    )
    hours = json.loads(text)

    for h in hours:
        day = ",".join(h.get("dayOfWeek"))
        start = h.get("opens")
        close = h.get("closes")

        if start != close:
            _tmp.append(f"{day}: {start} - {close}")
        else:
            _tmp.append(f"{day}: Closed")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.a1storage.com/"
    api_url = "https://inventory.g5marketingcloud.com/api/v1/locations?client_id=576&per_page=500"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["locations"]

    for j in js:
        street_address = j.get("street_address_1") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("home_page_url")
        location_name = j.get("name")
        phone = j.get("phone_number") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
