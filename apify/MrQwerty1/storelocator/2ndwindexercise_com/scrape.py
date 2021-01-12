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
    r = session.get("https://www.johnsonfitness.com/StoreLocator/Index?view_type=Home")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[contains(@class, 'single')]//h3/a/@href")


def get_data(page_url):
    locator_domain = "https://2ndwindexercise.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//span[@itemprop='name']/text()")).strip()
    if not location_name:
        return

    street_address = (
        " ".join(
            "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).split()
        )
        or "<MISSING>"
    )
    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].strip()
    if street_address.find("USA") != -1:
        street_address = street_address.split(",")[0].strip()

    city = (
        "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//p[@itemprop='address']/text()")).replace(",", "").strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//meta[@itemprop='latitude']/@content")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//meta[@itemprop='longitude']/@content")) or "<MISSING>"
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//meta[@itemprop='openingHours']/@content")) or "<MISSING>"
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
