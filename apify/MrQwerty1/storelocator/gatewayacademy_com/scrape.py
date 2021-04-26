import csv

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get(
        "https://www.cadence-education.com/cadence-locations-sitemap.xml",
        headers=headers,
    )
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://www.cadence-education.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
    street_address = (
        "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
        or "<MISSING>"
    )
    city = "".join(tree.xpath("//a[./span[@itemprop='streetAddress']]/text()")).strip()
    if city.endswith(","):
        city = city[:-1]
    state = (
        "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = page_url.split("/")[-2]
    phone = (
        "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"

    hours_of_operation = (
        " ".join("".join(tree.xpath("//li[@itemprop='openingHours']/text()")).split())
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
