import csv
import json

from concurrent import futures
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


def get_urls():
    r = session.get("https://www.perkinsrestaurants.com/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(), '/locations/')]/text()")


def get_data(page_url):
    locator_domain = "https://www.perkinsrestaurants.com/"
    if page_url.endswith("/locations/"):
        return

    slug = page_url.split("/")[-2]
    api = f"https://www.perkinsrestaurants.com/_data/locations/{slug}.json"
    r = session.get(api)
    j = r.json()
    path = j.get("path")
    j = j["content"]

    page_url = f"{locator_domain}{path}"
    location_name = j.get("name")
    street_address = j.get("address") or "<MISSING>"
    city = j.get("city") or "<MISSING>"
    state = j.get("state") or "<MISSING>"
    postal = j.get("zipcode") or "<MISSING>"
    country_code = j.get("country") or "<MISSING>"
    store_number = j.get("store_num") or "<MISSING>"
    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
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
    hours = j.get("hours") or []
    if hours:
        hours = hours[0]
        for d in days:
            part = d.lower()[:3]
            start = hours.get(f"{part}_open")
            if not start:
                continue
            end = hours.get(f"{part}_close")

            if start == end:
                _tmp.append(f"{d}: Closed")
            else:
                _tmp.append(f"{d}: {start} - {end}")

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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    session = SgRequests()
    scrape()
