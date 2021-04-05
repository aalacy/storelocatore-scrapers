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
    r = session.get("https://www.monicals.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//h4/a[@class='my-monicals']/@href")


def get_data(page_url):
    locator_domain = "https://www.monicals.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='title-wrap']/h2/text()")).strip()
    street_address = (
        "".join(tree.xpath("//li[@itemprop='streetAddress']/text()")).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = (
        "".join(tree.xpath("//input[@name='location_id']/@value")) or "<MISSING>"
    )
    phone = "".join(tree.xpath("//div[@class='phone']/text()")) or "<MISSING>"
    latitude = "".join(tree.xpath("//input[@id='location-lat']/@value")) or "<MISSING>"
    longitude = "".join(tree.xpath("//input[@id='location-lng']/@value")) or "<MISSING>"
    location_type = "<MISSING>"
    hours = tree.xpath(
        "//div[./h4[contains(text(), 'Location Hours')]]/p[.//*[contains(text(), '–')] or contains(text(), '–')]"
    )
    if hours:
        hours = hours[-1]
    else:
        hours = "<html></html>"
    hours_of_operation = (
        "".join(hours.xpath(".//text()"))
        .replace("\n", ";")
        .replace("WINTER: (Labor Day to Memorial Day);", "")
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
