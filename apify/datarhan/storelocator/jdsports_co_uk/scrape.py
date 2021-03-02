import csv
import json
from sglogging import SgLogSetup
from lxml import etree
from urllib.parse import urljoin
from urllib.request import urlopen, Request
from tenacity import retry, stop_after_attempt
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger('jdsports_co_uk')


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_location_data(url):
    html = get(url)
    if not html:
        return None

    dom = etree.HTML(html)
    data = dom.xpath(
        '//script[@type="application/ld+json" and contains(text(), "Store")]/text()'
    )[0]
    poi = json.loads(data)

    return poi


def fetch_location(url):
    store_url = urljoin('https://www.jdsports.co.uk', url)
    poi = fetch_location_data(store_url)
    if not poi:
        return None

    DOMAIN = "jdsports.co.uk"
    store_number = poi["url"].split("/")[-1]

    location_name = poi["name"]
    street_address = poi["address"]["streetAddress"]
    street_address = (
        street_address.replace("&amp;", "&") if street_address else "<MISSING>"
    )
    if street_address.endswith(","):
        street_address = street_address[:-1]
    city = poi["address"]["addressLocality"]
    city = city if city else "<MISSING>"
    state = poi["address"]["addressRegion"]
    state = state if state else "<MISSING>"
    zip_code = poi["address"]["postalCode"]
    zip_code = zip_code if zip_code else "<MISSING>"
    country_code = poi["address"]["addressCountry"]
    country_code = country_code if country_code else "<MISSING>"
    store_number = poi["url"].split("/")[-1]
    phone = poi["telephone"]
    if str(phone) == "0":
        phone = "<MISSING>"
    phone = phone if phone else "<MISSING>"
    location_type = poi["@type"]
    location_type = location_type if location_type else "<MISSING>"
    latitude = poi["geo"]["latitude"]
    latitude = latitude if latitude else "<MISSING>"
    longitude = poi["geo"]["longitude"]
    longitude = longitude if longitude else "<MISSING>"
    hours_of_operation = []
    for elem in poi["openingHoursSpecification"]:
        day = elem["dayOfWeek"]
        opens = elem["opens"]
        closes = elem["closes"]
        hours_of_operation.append(f"{day} {opens} - {closes}")
    hours_of_operation = (
        ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
    )

    return [
        DOMAIN,
        store_url,
        location_name,
        street_address,
        city,
        state,
        zip_code,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]


@retry(stop=stop_after_attempt(3))
def get(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        with urlopen(Request(url, headers=headers)) as session:
            return session.read()
    except Exception as e:
        logger.error(f'exception >>> {e}')
        if e.code == 404:
            return None
        raise e


def fetch_data():
    locations_url = "https://www.jdsports.co.uk/store-locator/all-stores/"
    dom = etree.HTML(get(locations_url))
    all_locations = dom.xpath('//a[@class="storeCard guest"]/@href')

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_location, url) for url in all_locations]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
