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
    r = session.get("https://titleboxingclub.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='location-bottom-link']/@href")


def get_data(page_url):
    locator_domain = "https://titleboxingclub.com/"

    session = SgRequests()
    r = session.get(page_url)
    if r.status_code == 410:
        return
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'ExerciseGym')]/text()")
    ).replace("[ , ", "[")
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("addressCountry") or "<MISSING>"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    if phone.lower().find("text") != -1:
        phone = phone.lower().split("text")[-1].replace(":", "").strip()
    g = j.get("geo")
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("openingHours") or []
    for h in hours:
        h = h.strip()
        if len(h) != 2:
            _tmp.append(h)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

    iscoming = tree.xpath("//span[@class='coming_soon']")
    if iscoming:
        hours_of_operation = "Coming Soon"

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
            try:
                row = future.result()
            except:
                row = []
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
