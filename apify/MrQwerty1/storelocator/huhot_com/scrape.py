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


def get_elements():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get("https://www.huhot.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='marker']")


def get_data(el):
    locator_domain = "https://www.huhot.com/"
    page_url = "".join(el.xpath("./@href"))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'openingHours') and @type='application/ld+json']/text()"
        )
    )

    j = json.loads(text)

    location_name = j.get("name").strip()
    a = j.get("address", {})
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    try:
        latitude, longitude = "".join(el.xpath("./@data-latlng")).split(",")
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = ";".join(j.get("openingHours", [])) or "<MISSING>"

    if hours_of_operation.find(":") == -1:
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

    return row


def fetch_data():
    out = []
    elements = get_elements()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, el): el for el in elements}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
