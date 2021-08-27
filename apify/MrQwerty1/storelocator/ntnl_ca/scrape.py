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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    r = session.get("https://www.ntnl.ca/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='Learn more']/@href")


def get_data(url):
    locator_domain = "https://www.ntnl.ca/"
    page_url = f"https://www.ntnl.ca{url}"
    country_code = "CA"
    store_number = "<MISSING>"
    location_type = "<MISSING>"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//div[@data-block-json]/@data-block-json"))
    location_name = "national on " + tree.xpath("//h2/text()")[0].strip()

    j = json.loads(text)["location"]
    if "westhills" in page_url:
        street_address = tree.xpath("//a[contains(@href, '/maps/place')]/text()")[
            0
        ].strip()[:-1]
        line = (
            tree.xpath("//a[contains(@href, '/maps/place')]/text()")[-1]
            .strip()
            .split(", ")
        )
        marker = "".join(tree.xpath("//a[contains(@href, '/maps/place')]/@href"))
        latitude, longitude = get_coords_from_google_url(marker)
    else:
        street_address = j.get("addressLine1")
        line = j.get("addressLine2").split(", ")
        latitude = j.get("markerLat")
        longitude = j.get("markerLng")

    city = line.pop(0).strip()
    state = line.pop(0).strip()
    try:
        postal = line.pop(0).strip()
    except:
        postal = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//p[./strong[contains(text(), 'contact us')]]/a[contains(@href, 'tel:')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )

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
    session = SgRequests()
    scrape()
