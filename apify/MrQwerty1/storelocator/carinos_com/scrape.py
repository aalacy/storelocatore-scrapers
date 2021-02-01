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
    r = session.get("https://www.carinos.com/locations/")
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'carinos.locations.list')]/text()")
    )
    text = text.split("carinos.locations.list = ")[1].split("carinos.")[0].strip()[:-1]
    js = json.loads(text)

    for j in js:
        urls.append(f'https://www.carinos.com{j.get("url")}')

    return urls


def get_data(page_url):
    locator_domain = "https://www.carinos.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//location-current")[0].get(":loc-query"))
    j = json.loads(text)

    location_name = j.get("name")
    street_address = (
        f'{j.get("address")} {j.get("address2") or ""}'.strip() or "<MISSING>"
    )
    city = j.get("city") or "<MISSING>"
    state = j.get("state") or "<MISSING>"
    postal = j.get("zip") or "<MISSING>"
    country_code = "US"
    store_number = j.get("storeIdentifier") or "<MISSING>"
    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("lat") or "<MISSING>"
    longitude = j.get("lng") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[@class='group-hour-day']")

    for d in divs:
        day = "".join(d.xpath("./div[@class='name-day']/text()")).strip()
        time = "".join(d.xpath(".//li//text()")).strip()
        _tmp.append(f"{day}: {time}")

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
