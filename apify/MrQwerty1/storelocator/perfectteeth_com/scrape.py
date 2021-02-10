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
    geo = dict()
    session = SgRequests()
    r = session.get(
        "https://www.perfectteeth.com/wp-content/themes/perfect-teeth/src/practices.json"
    )
    js = r.json()["features"]

    for j in js:
        urls.append(j["properties"]["permalink"])
        geo[str(j["id"])] = j["geometry"]["coordinates"]

    return urls, geo


def get_data(page_url, geo):
    locator_domain = "https://www.perfectteeth.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[@type='application/ld+json' and contains(text(), 'image')]/text()"
        )
    )
    j = json.loads(text)

    location_name = j.get("name").replace("&#038;", "&")
    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country = a.get("addressCountry") or "<MISSING>"
    if country == "United States":
        country_code = "US"
    else:
        country_code = country
    store_number = "".join(
        tree.xpath("//a[contains(@href, '/request-appointment?practice=')]/@href")
    ).split("=")[-1]
    phone = (
        "".join(tree.xpath("//a[@class='location-phone']/text()")).strip()
        or "<MISSING>"
    )
    try:
        longitude, latitude = geo[store_number]
    except KeyError:
        longitude, latitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    li = tree.xpath("//ul[contains(@class, 'location-hours')]/li")

    for l in li:
        day = "".join(l.xpath("./span[@class='hours-day']/text()")).strip()
        time = "".join(l.xpath("./span[@class='hours-time']/text()")).strip()
        if time:
            _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "Closed"

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
    urls, geo = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, geo): url for url in urls}
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
