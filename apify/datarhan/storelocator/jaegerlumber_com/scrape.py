from lxml import etree
from sglogging import SgLogSetup
from sgselenium import SgChrome
import time
import re
import csv
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("jaegerlumber_com")


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
    # Your scraper here
    items = []

    start_url = "https://www.jaegerlumber.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgChrome() as driver:

        driver.get(start_url)
        logger.info("Driver is loading the page, Please wait....!")
        time.sleep(20)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('.//p[a[contains(@href, "mailto")]]')
    for poi_html in all_locations:
        store_url = start_url
        raw_address = poi_html.xpath(".//following-sibling::p[1]/text()")
        if not raw_address:
            continue
        street_address = raw_address[0]
        if "For Jaeger Kitchens Division" in street_address:
            continue
        location_name = dom.xpath(
            '//p[contains(text(), "{}")]/preceding-sibling::h2[1]/text()'.format(
                street_address
            )
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        city = raw_address[1].split(", ")[0].strip()
        state = raw_address[1].split(", ")[-1].split()[0].strip()
        zip_code = raw_address[1].split(", ")[-1].split()[-1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = poi_html.xpath(
            './/preceding-sibling::p[contains(text(), "Phone:")][1]/text()'
        )
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            dom.xpath(
                '//iframe[contains(@src, "{}")]/@src'.format(
                    city.replace("Pt ", "").replace(" ", "+")
                )
            )[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        latitude = geo[-1]
        longitude = geo[0]
        hoo = poi_html.xpath(
            './/following-sibling::p[contains(text(), "Mon")][1]/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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

        items.append(item)

    return items


def scrape():
    logger.info("Scraping Started...")
    data = fetch_data()
    write_output(data)
    logger.info(f"Scraping Finished | Total Store Count: {len(data)}")


if __name__ == "__main__":
    scrape()
