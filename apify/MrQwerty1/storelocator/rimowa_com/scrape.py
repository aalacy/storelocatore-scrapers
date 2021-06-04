import csv
import json

from concurrent import futures
import country_converter as coco
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
    api_url = "https://www.rimowa.com/on/demandware.store/Sites-Rimowa-Site/en_US/GeoJSON-AllStores?filterServices=STORE"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "max-age=0, no-cache",
        "Referer": "https://www.rimowa.com/gb/en/storelocator",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()["features"]

    for j in js:
        j = j.get("properties")
        urls.append(f"https://www.rimowa.com/us/en/storedetails/-/-{j.get('ID')}")

    return urls


def get_data(page_url):
    locator_domain = "https://www.rimowa.com/"
    cc = coco.CountryConverter()

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'addressLocality')]/text()"))
    j = json.loads(text)

    location_name = j.get("name")
    page_url = r.url
    a = j.get("address") or {}

    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country = a.get("addressCountry") or "<MISSING>"
    country_code = cc.convert(names=[country], to="ISO2")
    store_number = "<MISSING>"
    phone = j.get("telePhone") or "<MISSING>"
    g = j.get("geo") or {}
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = j.get("@type") or "<MISSING>"
    hours_of_operation = j.get("openingHours") or "<MISSING>"

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

    for el in row:
        if el == "null":
            row[row.index(el)] = "<MISSING>"

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
