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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get("https://www.billmillerbbq.com/all-locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='wpsl-store-location']/a/@href")


def get_data(page_url):
    locator_domain = "https://www.billmillerbbq.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var wpslMap_0')]/text()"))
    text = text.split('"locations":')[1].split("};")[0]
    j = json.loads(text)[0]

    location_name = j.get("store")
    street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
    city = j.get("city") or "<MISSING>"
    state = j.get("state") or "<MISSING>"
    postal = j.get("zip") or "<MISSING>"
    country_code = "US"
    store_number = page_url.split("-")[-1].replace("/", "")
    try:
        phone = tree.xpath("//a[contains(@href, 'tel')]/text()")[0].strip()
    except IndexError:
        phone = "<MISSING>"
    latitude = j.get("lat") or "<MISSING>"
    longitude = j.get("lng") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    lines = tree.xpath("//h4/following-sibling::div[@class='row']")
    for l in lines:
        day = "".join(l.xpath("./span[1]/text()")).strip()
        time = "".join(l.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp) or "Coming Soon"
    if hours_of_operation == "Coming Soon":
        location_type = hours_of_operation

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
