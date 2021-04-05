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
    urls = []
    session = SgRequests()
    countries = ["us", "ca", "pr"]

    for c in countries:
        r = session.get(f"https://www.paylesscar.com/en/locations/{c}")
        tree = html.fromstring(r.text)
        urls += tree.xpath("//a[@class='pl-loc-subtitle']/@href")

    return urls


def get_data(url):
    locator_domain = "https://www.paylesscar.com/"
    page_url = f"https://www.paylesscar.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    script = "".join(tree.xpath("//script[contains(text(), '@context')]/text()"))
    j = json.loads(script)

    location_name = (
        tree.xpath("//span[@itemprop='name']/text()")[-1].strip() or "<MISSING>"
    )
    a = j.get("address", {})
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = (
        "".join(tree.xpath("//span[@itemprop='addressRegion']/text()"))
        .replace(",", "")
        .strip()
        or "<MISSING>"
    )
    postal = a.get("postalCode") or "<MISSING>"
    country = a.get("addressCountry") or "<MISSING>"
    if country == "Canada":
        country_code = "CA"
    else:
        country_code = "US"
    store_number = "<MISSING>"
    phone = a.get("telephone", "").replace("(1)", "").strip() or "<MISSING>"
    latitude, longitude = j.get("map").split("=")[-1].split(",") or (
        "<MISSING>",
        "<MISSING>",
    )
    location_type = (
        "".join(
            tree.xpath(
                "//div[./div/strong[contains(text(), 'Type')]]/div[@class='col-sm-7 col-xs-7']/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    hours_of_operation = j.get("openingHours", "").replace(",", ";") or "<MISSING>"

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
