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
    start_urls = [
        "https://www.jencaremed.com",
        "https://www.chenmedicalcenters.com",
        "https://www.dedicated.care",
    ]

    for start in start_urls:
        url = f"{start}/find-a-location/"
        r = session.get(url)
        tree = html.fromstring(r.text)
        counties = tree.xpath("//a[@class='results-list-item__link-wrap']/@href")

        for c in counties:
            req = session.get(c)
            root = html.fromstring(req.text)
            links = root.xpath(
                "//a[@class='button button--dark' and text()='View Location']/@href"
            )
            for link in links:
                urls.append(start + link)

    return urls


def get_data(page_url):
    locator_domain = "https://www.chenmed.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'MedicalClinic')]/text()"))
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    g = j.get("geo")
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = j.get("brand") or "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//h6[text()='Hours']/following-sibling::p/text()"))
        .replace("\n", " ")
        .replace("\r", ";")
        .strip()
        or "<MISSING>"
    )

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
