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
    urls = []
    session = SgRequests()
    for i in range(1, 5000):
        r = session.get(f"https://www.hussle.com/search?page={i}")
        tree = html.fromstring(r.text)
        links = tree.xpath("//a[@class='result__gym-name-link']/@href")
        for l in links:
            urls.append(f"https://www.hussle.com{l}")

        if len(links) < 20:
            break

    return urls


def get_data(page_url):
    locator_domain = "https://www.hussle.com/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@type='application/ld+json']/text()"))
    j = json.loads(text)

    location_name = j.get("name")
    phone = j.get("telephone") or "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    location_type = "<MISSING>"

    a = j.get("address") or {}
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"

    g = j.get("geo") or {}
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"

    _tmp = []
    hours = tree.xpath("//li[@class='col-xs-12 gym-details__list--opening-hours-item']")
    for h in hours:
        day = "".join(h.xpath("./div[1]/text()")).strip()
        time = "".join(h.xpath("./div[2]/text()")).strip()
        _tmp.append(f"{day}: {time}")

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
    scrape()
