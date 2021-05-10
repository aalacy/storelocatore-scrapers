from sglogging import SgLogSetup
from sgrequests import SgRequests
import csv
from lxml import html

logger = SgLogSetup().get_logger(logger_name="4icu_org")
session = SgRequests()

locator_domain_url = "https://www.4icu.org"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

MISSING = "<MISSING>"

UK_COUNTRY_CODES = [
    "uk",
    "united kingdom",
    "great britain",
    "gb",
    "england",
    "scotland",
    "wales",
]

FIELDS = [
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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def get_urls():
    url_a_to_z = "https://www.4icu.org/gb/a-z/"
    r_page_url = session.get(url_a_to_z, headers=headers)
    locations = html.fromstring(r_page_url.text, "lxml")
    urls_stores = locations.xpath(
        '//table/tbody/tr/td/a[starts-with(@href, "/reviews")]/@href'
    )
    logger.info(f"Number of Locations Found: {len(urls_stores)}")
    urls_stores = [f"{locator_domain_url}{url_store}" for url_store in urls_stores]
    return urls_stores


def fetch_data():
    url_stores = get_urls()
    items = []
    for url_data in url_stores:
        r_per_each_loc = session.get(url_data, headers=headers)
        data_per_loc = html.fromstring(r_per_each_loc.text, "lxml")
        locator_domain = locator_domain_url
        page_url = url_data
        logger.info(f"Scraping Data from: {url_data} ")
        location_name = data_per_loc.xpath('//span[@itemprop="name"]/strong/text()')
        location_name = "".join(location_name)
        location_name = location_name if location_name else MISSING
        logger.info(f"location_name: {location_name}")

        street_address = data_per_loc.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = "".join(street_address)
        street_address = street_address if street_address else MISSING
        logger.info(f"street_address: {street_address}")

        city = data_per_loc.xpath('//span[@itemprop="addressLocality"]/text()')
        city = "".join(city)
        city = city if city else MISSING
        logger.info(f"city: {city}")

        state = data_per_loc.xpath('//span[@itemprop="addressRegion"]/text()')
        state = "".join(state)
        state = state if state else MISSING
        logger.info(f"state: {state}")

        zipcode = data_per_loc.xpath('//span[@itemprop="postalCode"]/text()')
        zipcode = "".join(zipcode)
        zip = zipcode if zipcode else MISSING
        logger.info(f"zip: {zip}")

        country_code = ""
        country_code = data_per_loc.xpath('//meta[@name="description"]/@content')
        country_code = "".join(country_code).split(">")[0].strip()
        country_code = country_code if country_code else MISSING

        if country_code.lower() in UK_COUNTRY_CODES:
            country_code = "GB"

        store_number = ""
        store_number = store_number if store_number else MISSING

        phone = data_per_loc.xpath(
            '//tr[th[contains(text(), "Tel")]]/td/span[@itemprop="telephone"]/text()'
        )
        phone = "".join(phone)
        phone = phone if phone else MISSING
        logger.info(f"phone: {phone} \n\n")
        location_type = ""
        location_type = location_type if location_type else MISSING
        latitude = ""
        latitude = latitude if latitude else MISSING
        longitude = ""
        longitude = longitude if longitude else MISSING

        hours_of_operation = ""
        hours_of_operation = hours_of_operation if hours_of_operation else MISSING
        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(row)
    return items


def scrape():
    logger.info("Scraping Started...")
    data = fetch_data()
    logger.info(f"Scraping Finished | Total Store Count: {len(data)}")
    write_output(data)


if __name__ == "__main__":
    scrape()
