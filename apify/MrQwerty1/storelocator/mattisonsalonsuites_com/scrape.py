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
    session = SgRequests()
    r = session.get("https://www.mattisonsalonsuites.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@id,'button-id-') and contains(@href, '/location/')]/@href"
    )


def get_data(page_url):
    locator_domain = "https://www.mattisonsalonsuites.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h1[@class='page-header-title inherit']/text()")
    ).strip()
    street_address = (
        "".join(tree.xpath("//*[@class='company-info-address']/span/span[1]/text()"))
        .replace("\n", ", ")
        .strip()
    )
    if "We" in street_address:
        street_address = street_address.split("We")[0].strip()
    if "Summerfield Crossing North" in street_address:
        street_address = street_address.replace(
            "Summerfield Crossing North", ""
        ).strip()
    city = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[2]/text()")
    ).strip()
    state = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[3]/text()")
    ).strip()
    postal = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[4]/text()")
    ).strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//*[@class='company-info-phone']/span/a/text()")).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath(
        "//div[@class='locations-single-address']//span[@class='company-info-hours-day']/text()"
    )
    times = tree.xpath(
        "//div[@class='locations-single-address']//li[@class='company-info-hours-openclose']/text()"
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
