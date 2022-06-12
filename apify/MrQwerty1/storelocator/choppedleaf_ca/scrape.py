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
    r = session.get(
        "https://www.choppedleaf.ca/wp-admin/admin-ajax.php?action=get_google_map_data&query=s%3D"
    )
    js = r.json()["data"]

    for j in js:
        urls.append(j["info"]["permalink"])

    return urls


def get_data(page_url):
    locator_domain = "https://www.choppedleaf.ca/"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = (
        "".join(tree.xpath("//div[@data-data]/@data-data"))
        .replace("[", "")
        .replace("]", "")
    )
    j = json.loads(text)
    i = j.get("info") or {}
    c = i.get("contact") or {}
    p = j.get("position") or {}

    location_name = i.get("post_title")
    source = i.get("address") or "<html></html>"
    root = html.fromstring(source)

    street_address = "".join(
        root.xpath("//span[@class='address-street']/text()")
    ).strip()
    city = "".join(root.xpath("//span[@class='address-city']/text()")).strip()
    state = "".join(root.xpath("//span[@class='address-province']/text()")).strip()
    postal = "<MISSING>"
    country_code = "CA"
    store_number = j.get("id") or "<MISSING>"
    phone = c.get("phone") or "<MISSING>"
    latitude = p.get("lat") or "<MISSING>"
    longitude = p.get("lng") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hh = c.get("hours") or "<html></html>"
    hours_tree = html.fromstring(hh)
    hours = hours_tree.xpath("//text()")
    black = ["May", "Can", "Jul", "Dec", "Holiday", "Jan", "Aug", "Oct"]

    for h in hours:
        if not h.strip():
            continue
        for b in black:
            if b in h:
                break
        else:
            _tmp.append(h.strip())
        if "TEMP" in h:
            break

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if "coming" in page_url:
        hours_of_operation = "Coming Soon"

    if "Temp" in location_name:
        hours_of_operation = "Temporarily Closed"

    if state == "Washington":
        country_code = "US"

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
    session = SgRequests()
    scrape()
