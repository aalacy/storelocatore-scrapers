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
    r = session.get("https://www.californiafamilyfitness.com/gyms/gym-finder")
    tree = html.fromstring(r.text)

    return tree.xpath("//p/a[contains(@href, '/gyms/')]/@href")


def get_data(url):
    locator_domain = "https://www.californiafamilyfitness.com/"
    page_url = f"https://www.californiafamilyfitness.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath(
            "//div[@class='location-contact location--contact-info']/meta[@itemprop='name']/@content"
        )
    )
    street_address = (
        "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
        or "<MISSING>"
    )
    if street_address.endswith(","):
        street_address = street_address[:-1]
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
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    hours_of_operation = (
        " ".join(
            tree.xpath(
                "//*[contains(text(), 'HOURS OF OPERATION')]/following-sibling::*//text()"
            )
        )
        or "<MISSING>"
    )
    if "*" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("*")[0].strip()
    if "FAMILY" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("FAMILY")[0].strip()
    isclosed = tree.xpath(
        "//strong[contains(text(), 'closed')]|//strong[contains(text(), 'reopen')]"
    )
    if isclosed:
        hours_of_operation = "Temporarily Closed"

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
