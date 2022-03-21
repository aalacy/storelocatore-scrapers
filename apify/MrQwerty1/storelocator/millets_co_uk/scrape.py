import re
import csv
import json

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("millets_co_uk")


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
    r = session.get("https://www.millets.co.uk/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[contains(@id, 'brands_')]//a/@href")


def fetch_page_schema(session, url):
    r = session.get(url)
    tree = html.fromstring(r.text)
    src = tree.xpath("//script[contains(@src, 'yextpages.net')]/@src").pop()
    r = session.get(src)

    match = re.search(r"Yext._embed\((.*)\n?\)", r.text, re.IGNORECASE)
    if not match:
        logger.error("unable to parse")

    data = json.loads(match.group(1))
    entity = data["entities"].pop()
    return entity["schema"]


def get_data(url, session):
    locator_domain = "https://www.millets.co.uk/"
    page_url = f"https://www.millets.co.uk{url}"
    data = fetch_page_schema(session, page_url)

    a = data.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "GB"

    location_name = f"{data.get('name')} {city}"
    store_number = data.get("@id") or "<MISSING>"
    phone = data.get("telephone") or "<MISSING>"

    geo = data.get("geo")
    latitude = geo.get("latitude") or "<MISSING>"
    longitude = geo.get("longitude") or "<MISSING>"
    location_type = data.get("@type").pop()

    hours_of_operation = []
    for time in data.get("openingHoursSpecification"):
        day = time["dayOfWeek"]
        opens = time.get("opens")
        closes = time.get("closes")
        if opens and closes:
            hours_of_operation.append(f"{day}: {opens}-{closes}")
    hours_of_operation = ",".join(hours_of_operation) or "<MISSING>"

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
    session = SgRequests()
    session.get("https://www.millets.co.uk/stores")

    with futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(get_data, url, session): url for url in urls}
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
