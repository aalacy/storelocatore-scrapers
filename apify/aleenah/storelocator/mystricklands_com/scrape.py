from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup
from lxml import html
import re
import csv


logger = SgLogSetup().get_logger("mystricklands_com")


MISSING = "<MISSING>"
session = SgRequests()


def get_locations():
    viewmodel = session.get(
        "https://siteassets.parastorage.com/singlePage/viewerViewModeJson?&isHttps=true&isUrlMigrated=true&metaSiteId=4fb1a8a3-6d99-4330-b844-2d336bff969a&quickActionsMenuEnabled=false&siteId=023f2d1c-56de-438a-91d6-0b7a4fa6f584&v=3&pageId=5eaf97_92e55dbfa2e20f2249a6b7f6033465df_644&module=viewer-view-mode-json&moduleVersion=1.279.0&viewMode=desktop&dfVersion=1.1027.0"
    ).json()

    document_data = viewmodel.get("data").get("document_data")

    for key, item in document_data.items():
        locations_matcher = re.compile("locations", re.IGNORECASE)
        label = item.get("label", None)

        if label and locations_matcher.match(label):
            location_menu_items = item.get("items")

    if not location_menu_items:
        raise Exception("cannot find locations")

    menu_keys = [item.replace("#", "") for item in location_menu_items]
    link_keys = [
        document_data.get(item).get("link").replace("#", "") for item in menu_keys
    ]
    page_items = [
        document_data.get(key).get("pageId").replace("#", "") for key in link_keys
    ]

    page_links = [document_data.get(key).get("pageUriSEO") for key in page_items]

    return [f"https://www.mystricklands.com/{location}" for location in page_links]


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "location_type",
                "store_number",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "latitude",
                "longitude",
                "phone",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            if row:
                writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r"destination=[-?\d\.]*\,([-?\d\.]*)", url)[0]
    lat = re.findall(r"destination=(-?[\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    locator_domain = "mystricklands.com"
    logger.info("Pulling Store URLs")
    page_urls = get_locations()
    logger.info(f"Number of Store URLs: {len(page_urls)}")
    total = 0
    for page_url in page_urls:
        response = session.get(page_url)
        logger.info(f"Pulling the data from: {page_url}")
        bs4 = BeautifulSoup(response.text, "lxml")
        location_name = bs4.select_one("h2 span").text
        address_data = bs4.find_all("main", {"id": "PAGES_CONTAINER"})
        address_data = [" ".join(i.text.strip().split()) for i in address_data]
        address_data = [" ".join(i.split()) for i in address_data]
        address_data = [i for i in address_data if i]
        address_data = " ".join(address_data)
        matched = re.search(r"(\d+\s.+(?:,|\\n)?.*),\s(\w{2})\s(\d{5})", address_data)
        if matched:
            address_clean = (
                f"{matched.group(1)}, {matched.group(2)}, {matched.group(3)}"
            )
            address_clean = address_clean.replace(
                "2021 SEASONClick Here for Flavor of the Day", ""
            )
            logger.info(f"Full Address: {address_clean}")
            paddress = parse_address_intl(address_clean)
            street_address = paddress.street_address_1 or "<MISSING>"
            city = paddress.city or "<MISSING>"
            state = paddress.state or "<MISSING>"
            zipcode = paddress.postcode or "<MISSING>"
        else:
            street_address = "<INACCESSIBLE>"
            city = "<INACCESSIBLE>"
            state = "<INACCESSIBLE>"
            zipcode = "<INACCESSIBLE>"
        country_code = "US"
        phone_match = re.search(
            r"Phone:\s*\((\d{3})\).*(\d{3})-(\d{4})", address_data, re.IGNORECASE
        )

        phone = (
            f"{phone_match.group(1)}{phone_match.group(2)}{phone_match.group(3)}"
            if phone_match
            else MISSING
        )

        hours_of_operation = MISSING
        raw_data = html.fromstring(response.text, "lxml")
        open_daily = raw_data.xpath(
            '//*[contains(text(), "Daily")]/text()|//p[span[span[contains(text(), "Daily")]]]//text()'
        )
        open_daily = "".join(open_daily)
        open_daily = " ".join(open_daily.split())
        logger.info(f"Open Daily: {open_daily}")
        store_hours_1 = raw_data.xpath('//span[contains(text(), "Sunday")]//text()')
        store_hours_2 = raw_data.xpath('//span[contains(text(), "Friday")]//text()')
        store_hours = f"{''.join(store_hours_1)}; {''.join(store_hours_2)}"

        if open_daily:
            hours_of_operation = open_daily
        else:
            if store_hours_1 and store_hours_2:
                hours_of_operation = store_hours
            else:
                hours_of_operation = MISSING

        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
        store_number = MISSING
        yield [
            locator_domain,
            page_url,
            location_name,
            location_type,
            store_number,
            street_address.strip(),
            city,
            state,
            zipcode,
            country_code,
            latitude,
            longitude,
            phone,
            hours_of_operation,
        ]
        total += 1
    logger.info(f"Scraping Finished | Total Store Count: {total} ")


def scrape():
    logger.info("Scraping Started")
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
