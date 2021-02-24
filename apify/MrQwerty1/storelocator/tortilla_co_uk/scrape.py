import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
    r = session.get("https://www.tortilla.co.uk/locations-overview/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='GTM-Tracking-Location-Listing-Page-Restaurant-Location-Link']/@href"
    )


def get_data(page_url):
    locator_domain = "https://www.tortilla.co.uk/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='b-location-header-inner__title']/text()")
    ).strip()
    line = "".join(
        tree.xpath(
            "//span[text()='Contact']/following-sibling::p[1]//text()|//div[@class='b-location-info-right-coming-soon-contact']/p//text()"
        )
    ).strip()

    postal = " ".join(line.split()[-2:])
    line = line.replace(postal, "").strip()
    if line.endswith(","):
        line = line[:-1]

    adr = parse_address(International_Parser(), line, postcode=postal)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )

    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    store_number = (
        "".join(tree.xpath("//div[@data-postid]/@data-postid")) or "<MISSING>"
    )
    if store_number == "<MISSING>":
        return
    phone = (
        "".join(
            tree.xpath(
                "//div[@class='b-location-info-contact']//a[contains(@href, 'tel')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lng]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"

    hours = tree.xpath("//span[text()='Opening Hours']/following-sibling::p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or "Closed"

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
