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
    r = session.get("https://www.steppingstoneschool.com/find-a-school/")
    tree = html.fromstring(r.text)
    text = tree.xpath("//script[contains(text(), 'campuses.splice')]/text()")
    for t in text:
        t = t.split(", 0, ")[-1].split(");")[0]
        j = json.loads(t)
        slug = j.get("campus_slug")
        lat = j.get("lat") or "<MISSING>>"
        lng = j.get("lng") or "<MISSING>"
        geo[slug] = {"lat": lat, "lng": lng}
        urls.append(f"https://www.steppingstoneschool.com/campuses/{slug}")

    return geo, urls


def get_data(page_url, geo):
    locator_domain = "https://www.steppingstoneschool.com/"
    slug = page_url.replace("https://www.steppingstoneschool.com/campuses/", "")
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@id='campus_name']/text()")).strip()
    street_address = (
        ", ".join(tree.xpath("//li[./i[@class='fa fa-map-marker']]/text()")).strip()
        or "<MISSING>"
    )
    line = "".join(tree.xpath("//li[@class='second_address_line']/text()")).strip()
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//li[./i[@class='fa fa-phone']]/text()")).strip()
        or "<MISSING>"
    )
    latitude = geo[slug].get("lat")
    longitude = geo[slug].get("lng")
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//li[./i[@class='fa fa-clock-o']]/text()")).strip()
        or "<MISSING>"
    )

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
    geo, urls = get_urls()

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
