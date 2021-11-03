import csv
import re

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
    r = session.get("https://rockbottom.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//h3/a/@href")


def get_data(page_url):
    locator_domain = "https://rockbottom.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/strong/text()")).strip()
    street_address = (
        tree.xpath("//span[@class='street-address']/text()")[0].strip() or "<MISSING>"
    )
    city = tree.xpath("//span[@class='locality']/text()")[0].strip() or "<MISSING>"
    state = tree.xpath("//span[@class='region']/text()")[0].strip() or "<MISSING>"
    postal = tree.xpath("//span[@class='postal-code']/text()")[0].strip() or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = tree.xpath("//p[@class='tel']/text()")[0].strip() or "<MISSING>"
    text = "".join(tree.xpath("//script[contains(text(), 'http://schema.org')]/text()"))
    latitude = "".join(re.findall(r'"latitude": (\d+.\d+)', text)) or "<MISSING>"
    longitude = "".join(re.findall(r'"longitude": (-?\d+.\d+)', text)) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[@class='hour__group operating_hours']/div")

    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        time = "".join(d.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
