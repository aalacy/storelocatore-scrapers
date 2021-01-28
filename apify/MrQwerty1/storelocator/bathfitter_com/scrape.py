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
    r = session.get("https://www.bathfitter.com/us-en/locations-list/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='ColumnsWrapper']//a/@href")


def get_data(url):
    session = SgRequests()
    locator_domain = "https://www.bathfitter.com/"

    if url.startswith("http"):
        return
    page_url = f"https://www.bathfitter.com{url}"

    try:
        r = session.get(page_url)
    except:
        return

    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@type='application/ld+json']/text()"))
    js = json.loads(text)

    location_name = "".join(tree.xpath("//div[@class=' bf-location-info']/h2/text()"))
    a = js.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("addressCountry").get("name") or "<MISSING>"

    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[@class='bf-li-item_phone']/text()")).strip()
        or "<MISSING>"
    )
    g = js.get("geo") or {}
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//ul[@class='hours-wrap']/li")
    for h in hours:
        day = "".join(h.xpath("./span[@class='day']/text()")).strip()
        time = "".join(h.xpath("./span[@class='bf-hours']/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.lower().count("closed") == 7:
        hours_of_operation = "Closed"

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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
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
