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
    r = session.get("https://www.ntnl.ca/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='Learn more']/@href")


def get_data(url):
    locator_domain = "https://www.ntnl.ca/"
    page_url = f"https://www.ntnl.ca{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//div[@data-block-json]/@data-block-json"))
    j = json.loads(text)["location"]

    location_name = j.get("addressTitle")
    street_address = j.get("addressLine1")
    line = j.get("addressLine2").split(", ")
    city = line.pop(0).strip()
    state = line.pop(0).strip()
    postal = line.pop(0).strip()
    country_code = "CA"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//p[./strong[contains(text(), 'contact us')]]/a[contains(@href, 'tel:')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = j.get("markerLat")
    longitude = j.get("markerLng")
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//p[./strong[contains(text(), 'hours')]]/strong/text()")[1:]
    times = tree.xpath("//p[./strong[contains(text(), 'hours')]]/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "Temporarily Closed"

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
