import csv
import json
from lxml import etree
from urllib.parse import urljoin
from sgrequests import SgRequests
from sglogging import sglog
import os

log = sglog.SgLogSetup().get_logger(
    logger_name="jdsports.co.uk", stdout_log_level="INFO"
)

HEADERS_LIST_PAGE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Host": "www.jdsports.co.uk",
    "TE": "Trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}

HEADERS_STORE_PAGE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Host": "www.jdsports.co.uk",
    "Referer": "https://www.jdsports.co.uk/store-locator/all-stores/",
    "TE": "Trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}


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


def fetch_data():
    os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"

    items = []
    scraped_stores = []

    DOMAIN = "jdsports.co.uk"
    start_url = "https://www.jdsports.co.uk/store-locator/all-stores/"

    response_text = get_page(start_url, HEADERS_LIST_PAGE)
    dom = etree.HTML(response_text)

    try:
        all_locations = dom.xpath('//a[@class="storeCard guest"]/@href')
    except:
        # TODO - if it was not "Access Denied", but some other unexpected page !!
        exit(response_text)

    for url in all_locations:
        store_url = urljoin(start_url, url)

        response_text = get_page(store_url, HEADERS_STORE_PAGE)
        loc_dom = etree.HTML(response_text)

        try:
            data = loc_dom.xpath(
                '//script[@type="application/ld+json" and contains(text(), "Store")]/text()'
            )[0]
        except:
            # TODO - if it was not "Access Denied", but some other unexpected page !!
            exit(response_text)

        poi = json.loads(data)

        location_name = poi["name"]
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
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

        item = [
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

        log.info("Store page done")

        check = "{} {}".format(store_number, street_address)
        if check not in scraped_stores:
            scraped_stores.append(check)
            items.append(item)

    return items


def get_page(page_url, headers):
    access_denied_text = "Access Denied"
    response_text = access_denied_text

    i = 1

    # TODO set best value ??
    max_tries = 10
    while access_denied_text.lower() in response_text.lower():
        session = SgRequests()

        if i > 1:
            log.info(f"Got {access_denied_text}. Retrying...")

        log.info(f"Requesting page: {page_url}")

        response = session.get(page_url, headers=headers)
        response_text = response.text

        # if proxy did not work for max_tries times in a row
        if i >= max_tries:
            exit(
                f"{i} different IPs failed to access {page_url}. Is Proxy working correctly ?"
            )

        i += 1

    return response_text


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
