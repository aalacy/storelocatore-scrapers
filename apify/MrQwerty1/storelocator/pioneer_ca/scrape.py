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
    r = session.get("https://www.pioneer.ca/sitemap-stores.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://www.pioneer.ca/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h2[@class='station__title']/text()")).strip()
    line = tree.xpath("//span[@class='station__coordinates-line']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.replace(state, "").strip()
    country_code = "CA"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[@class='station__coordinates-line']/text()")).strip()
        or "<MISSING>"
    )
    try:
        text = "".join(tree.xpath("//script[contains(text(), 'lat:')]/text()"))
        latitude = re.search(r"lat: (.*?),", text).group(1)
        longitude = re.search(r"lng: (.*)", text).group(1)
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    hours_of_operation = "<MISSING>"
    if tree.xpath("//img[@alt='24h clock']"):
        hours_of_operation = "24 hours"

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
