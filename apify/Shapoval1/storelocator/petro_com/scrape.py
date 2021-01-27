import csv
import json
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
    r = session.get("https://www.petro.com/petro-locations")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//ul[@class='sectionMenu']/li[not(@class)]/a[contains(@href, '/petro-locations')]/@href"
    )


def get_data(url):
    locator_domain = "https://www.petro.com"
    page_url = f"https://www.petro.com{url}"
    if url.startswith("https"):
        page_url = url
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath('//script[contains(.,"LocalBusiness")]/text()'))

    j = json.loads(text)[0]
    ad = j.get("address")
    street_address = ad.get("streetAddress") or "<MISSING>"
    city = ad.get("addressLocality") or "<MISSING>"
    state = ad.get("addressRegion") or "<MISSING>"
    postal = ad.get("postalCode") or "<MISSING>"
    country_code = "US"

    store_number = "<MISSING>"
    page_url = j.get("url") or "<MISSING>"
    location_name = j.get("name") or "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
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
    s = set()
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                checkout = row[1]
                if checkout not in s:
                    s.add(checkout)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
