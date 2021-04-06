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
    session = SgRequests()
    r = session.get("https://www.millets.co.uk/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[contains(@id, 'brands_')]//a/@href")


def get_data(url):
    locator_domain = "https://www.millets.co.uk/"
    page_url = f"https://www.millets.co.uk{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'LocalBusiness')]/text()")
    ).strip()
    if not text:
        return
    j = json.loads(text)

    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "GB"

    location_name = f"{j.get('name')} {city}"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    text = j.get("hasmap") or "@<MISSING>,<MISSING>"
    latitude = text.split("@")[1].split(",")[0]
    longitude = text.split("@")[1].split(",")[1]
    location_type = "<MISSING>"
    hours_of_operation = ";".join(j.get("openingHours")) or "<MISSING>"

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
    scrape()
