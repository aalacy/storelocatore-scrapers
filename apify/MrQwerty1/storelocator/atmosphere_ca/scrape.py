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
    r = session.get("https://www.atmosphere.ca/sitemap_stores01.xml", headers=headers)
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://www.atmosphere.ca/"

    try:
        r = session.get(page_url, headers=headers, timeout=20)
    except:
        return

    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//h1/text()")).strip()
    text = "".join(tree.xpath("//div[@data-info]/@data-info"))
    j = json.loads(text)

    street_address = "".join(
        tree.xpath("//div[@class='sdt-store-details__descr']/text()")
    ).strip()
    if street_address.endswith(","):
        street_address = street_address[:-1]

    a = j.get("address")
    city = a.get("town") or "<MISSING>"
    state = a.get("province") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "CA"
    store_number = j.get("storeId") or "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[@class='sdt-store-details__phone']/text()")).strip()
        or "<MISSING>"
    )
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"
    _tmp = []
    hours = tree.xpath(
        "//div[@class='accordion-item-wrap drawer-ui'][1]//div[contains(@class, 'store-hours__content')]/p/text()"
    )
    for h in hours:
        if "hours" in h.lower():
            break
        if h.strip():
            _tmp.append(f" {h}")
        else:
            _tmp.append(";")

    hours_of_operation = "".join(_tmp).strip() or "<MISSING>"
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

    with futures.ThreadPoolExecutor(max_workers=45) as executor:
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
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }
    scrape()
