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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    session = SgRequests()
    r = session.get("https://www.clubmetrousa.com/")
    tree = html.fromstring(r.text)

    return set(
        tree.xpath("//a[./span[text()='Locations']]/following-sibling::ul[1]//a/@href")
    )


def get_data(page_url):
    locator_domain = "https://www.clubmetrousa.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = tree.xpath("//script[contains(text(), 'ExerciseGym')]/text()")[-1]
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[contains(@href, 'tel:')]/@href"))
        .replace("tel:", "")
        .strip()
        or "<MISSING>"
    )
    line = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(line)
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//p[@class='text-center' and ./strong]|//p[@class='text-center' and ./strong]/following-sibling::p"
    )

    for h in hours:
        line = " ".join("".join(h.xpath(".//text()")).split())
        if "*" in line:
            continue
        _tmp.append(line)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.endswith(";"):
        hours_of_operation = hours_of_operation[:-1]

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
