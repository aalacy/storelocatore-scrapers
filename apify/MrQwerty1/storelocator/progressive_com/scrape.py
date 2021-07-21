import csv
import usaddress
import time
from concurrent import futures
from lxml import html
from sgrequests import SgRequests

from sglogging import sglog

DOMAIN = "progressive.com"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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


def get_address(line):
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_states():
    r = session.get("https://www.progressive.com/agent/local-agent/")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@class='state-list']/li/a/@href")


def get_cities(state):
    log.info(f"State:: {state}")
    r = session.get(state)
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@class='city-list']/li/a/@href")


def get_page(city):
    log.info(f"City:: {city}")
    r = session.get(city)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='list-link details']/@href")


def get_urls():
    states = get_states()
    cities = []
    urls = []

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(get_cities, state): state for state in states}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            cities += rows

    states.clear()
    with futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(get_page, city): city for city in cities}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            urls += rows

    cities.clear()

    return urls


def get_data(page_url):
    locator_domain = DOMAIN
    log.info(f"Grabbing From: {page_url}")
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = "".join(
        tree.xpath("//dt[text()='Address:']/following-sibling::dd/text()")
    ).strip()

    try:
        street_address, city, state, postal = get_address(line)
    except usaddress.RepeatedLabelError:
        street_address = line.split(",")[0].strip()
        city = line.split(",")[1].strip()
        line = line.split(",")[-1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//dt[text()='Phone:']/following-sibling::dd/a/text()")
        ).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//div[./h2[text()='Office Hours']]/following-sibling::div[1]//dl/div"
    )
    for h in hours:
        day = "".join(h.xpath("./dt/text()")).strip()
        time = "".join(h.xpath("./dd/text()")).strip()
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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                check = tuple(row[2:7])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    log.info("Scraping Started")
    start = time.time()
    data = fetch_data()
    write_output(data)
    end = time.time()
    log.info(f"Total Locations added = {len(data)}")
    log.info(f"It took {end-start} seconds to complete the crawl.")


if __name__ == "__main__":
    session = SgRequests()
    scrape()
