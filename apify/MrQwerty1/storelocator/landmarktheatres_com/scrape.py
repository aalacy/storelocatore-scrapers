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
    r = session.get("https://www.landmarktheatres.com/?portal")
    tree = html.fromstring(r.text)
    aa = tree.xpath("//a[@class='accordion-region-link']")
    for a in aa:
        _id = "".join(a.xpath("./@data-accordion-region-id"))
        region = "".join(a.xpath("./@data-accordion-region-link"))
        r = session.get(f"https://www.landmarktheatres.com/api/CinemasByRegion/{_id}")
        js = r.json()
        for j in js:
            slug = j.get("FriendlyName")
            urls.append(f"https://www.landmarktheatres.com/{region}/{slug}/info")

    return urls


def get_data(page_url):
    locator_domain = "https://www.bangor.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//span[@class='header-theatre-location']/text()")
    ).strip()
    line = "".join(
        tree.xpath("//div[@class='header-theatre-group-middle']/a/text()")
    ).strip()
    street_address = line.split(",")[0].strip()
    city = line.split(",")[-3].strip()
    state = line.split(",")[-2].strip()
    postal = line.split(",")[-1].strip()

    if state.find("Washington") != -1:
        city = "Washington"
        state = "WA"

    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//p[@class=' ta_c']/text()")[-2].strip() or "<MISSING>"
    except IndexError:
        phone = "<MISSING>"

    div = "".join(tree.xpath("//div[@data-map]/@data-map"))
    j = json.loads(div)
    latitude = j.get("lat") or "<MISSING>"
    longitude = j.get("lng") or "<MISSING>"
    location_type = "<MISSING>"

    hours_of_operation = "<MISSING>"

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
