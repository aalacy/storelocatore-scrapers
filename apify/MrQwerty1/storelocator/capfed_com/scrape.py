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
    r = session.get("https://www.capfed.com/locations/branch-locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='location-search__result-name']/@href")


def get_data(url):
    locator_domain = "https://www.capfed.com/"
    page_url = f"https://www.capfed.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@class=' hero__heading']/text()")).strip()
    street_address = (
        ", ".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
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
    store_number = "<MISSING>"
    try:
        phone = (
            tree.xpath("//span[@itemprop='telephone']/text()")[0].strip() or "<MISSING>"
        )
    except IndexError:
        phone = "<MISSING>"
    latitude = (
        "".join(tree.xpath("//div[@data-latitude]/@data-latitude")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//div[@data-latitude]/@data-longitude")) or "<MISSING>"
    )
    location_type = "Branch"

    _tmp = []
    hours = tree.xpath(
        "//div[@class='location-details__hours' and ./h2[contains(text(), 'Lobby')]]/text()"
    )

    for h in hours:
        if h.strip():
            _tmp.append(f"{h.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if location_name.lower().find("soon") != -1:
        hours_of_operation = "Coming Soon"

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
