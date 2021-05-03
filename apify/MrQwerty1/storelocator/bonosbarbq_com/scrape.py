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
    r = session.get("https://www.bonosbarbq.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='image-box-wrap hasOverlay']/a/@href")


def get_data(page_url):
    locator_domain = "https://www.bonosbarbq.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='section-heading']/h3/text()")
    ).strip()
    line = tree.xpath("//div[@class='info']/p[1]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//div[@class='info']/p[2]/text()")[0].split(":")[-1].strip()
    except IndexError:
        phone = "<MISSING>"

    text = "".join(tree.xpath("//script[contains(text(),'zoom_position')]/text()"))
    text = text.split('"zoom_position":')[1].split(',"group_markers"')[0]
    js = json.loads(text)
    latitude = js.get("lat")
    longitude = js.get("lng")
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
