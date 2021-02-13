import csv
import re

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
    r = session.get("https://kingsfoodmarkets.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='View Store Details']/@href")


def get_data(url):
    locator_domain = "https://kingsfoodmarkets.com/"
    page_url = f"https://kingsfoodmarkets.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath(
            "//span[@class='field field--name-title field--type-string field--label-hidden']/text()"
        )
    ).strip()
    street_address = (
        "".join(tree.xpath("//span[@class='address-line1']/text()")).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@class='locality']/text()")).strip() or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@class='administrative-area']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@class='postal-code']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//div[@class='field field--name-field-phone field--type-string field--label-inline clearfix']/div/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = "".join(re.findall(r'"lat":(\d+.\d+)', r.text)) or "<MISSING>"
    longitude = "".join(re.findall(r'"lon":(-?\d+.\d+)', r.text)) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath(
        "//div[@class='section']//div[@class='field field--name-field-days field--type-string field--label-hidden field__item']/text()"
    )
    times = tree.xpath(
        "//div[@class='section']//div[@class='field field--name-field-times field--type-string field--label-hidden field__item']/text()"
    )
    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

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
