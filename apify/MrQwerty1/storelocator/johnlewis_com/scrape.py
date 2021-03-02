import csv
import json

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
    r = session.get("https://www.johnlewis.com/our-shops")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='store-locator-list__store-link']/@href")


def get_data(url):
    locator_domain = "https://www.johnlewis.com/"
    page_url = f"https://www.johnlewis.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join(
        "".join(tree.xpath("//h1[@class='shop-title']//text()")).split()
    )
    line = "".join(tree.xpath("//p[@class='shop-details-address']/text()")).strip()
    postal = " ".join(line.split()[-2:])
    if postal.find("London") != -1:
        postal = postal.split()[-1].strip()
    line = line.replace(postal, "").strip()
    adr = parse_address(International_Parser(), line, postcode=postal)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )

    city = adr.city or "<MISSING>"
    if city == "<MISSING>":
        city = location_name.split(",")[-1].strip()

    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//span[@class='shop-details-telephone-number']/text()")
        ).strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//script[@id='jsonPageData']/text()")) or "{}"
    js = json.loads(text)
    latitude = js.get("latitude") or "<MISSING>"
    longitude = js.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//dt[@class='opening-day']/text()")
    times = tree.xpath("//dd[@class='opening-time']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp).replace("*", "") or "<MISSING>"
    if hours_of_operation.count("Temporarily Closed") == 7:
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
