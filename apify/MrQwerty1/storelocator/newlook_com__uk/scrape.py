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
    r = session.get("https://www.newlook.com/uk/sitemap/maps/sitemap_uk_pos_en_1.xml")
    tree = html.fromstring(r.content)

    return tree.xpath(
        "//loc[contains(text(), 'https://www.newlook.com/uk/store/')]/text()"
    )


def get_data(page_url):
    locator_domain = "https://www.newlook.com/"
    if page_url.lower().find("closed") != -1:
        return

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='store-hours']/text()"))
    if not text:
        return

    j = json.loads(text)
    location_name = j.get("name")
    a = j.get("address") or {}
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "GB"
    store_number = page_url.split("-")[-1]
    phone = j.get("telephone") or "<MISSING>"
    g = j.get("geo") or {}
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("openingHoursSpecification") or []

    for h in hours:
        day = h.get("dayOfWeek").split("/")[-1]
        start = h.get("opens")
        close = h.get("closes")
        if start != close:
            _tmp.append(f"{day}: {start} - {close}")
        else:
            _tmp.append(f"{day}: Closed")
    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    message = "".join(tree.xpath("//p[@class='store-results__message']/text()")).strip()
    if message.lower().find("closed") != -1:
        location_type = message

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

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
