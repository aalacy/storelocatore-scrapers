import csv
from lxml import etree
from time import sleep

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("minex_com")


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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "linex.com"
    start_url = "https://linex.com/find-a-location"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )

    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        driver.get(start_url)
        sleep(5)
        driver.find_element_by_xpath(
            '//span[contains(text(), "International")]'
        ).click()
        sleep(5)
        logger.info("International Clicked")
        driver.find_element_by_xpath(
            '//span[contains(text(), "United States")]'
        ).click()
        logger.info("United States Clicked")
        for code in all_codes:
            driver.find_element_by_xpath('//input[@name="location"]').send_keys(code)
            sleep(2)
            logger.info("zipcode - send_keys executed")
            driver.find_element_by_xpath('//button[contains(text(), "Search")]').click()
            sleep(20)
            logger.info(" Search Button Clicked")
            driver.find_element_by_xpath('//input[@name="location"]').clear()

            code_dom = etree.HTML(driver.page_source)
            all_locations += code_dom.xpath('//div[@class="find-result "]')

    for loc_html in list(set(all_locations)):
        store_url = loc_html.xpath('.//a[contains(text(), "Visit Website")]/@href')
        store_url = (
            store_url[0].strip().replace(" ", "").replace("http://https", "https")
            if store_url
            else "<MISSING>"
        )

        location_type = "<MISSING>"
        hours_of_operation = ""

        if store_url != "<MISSING>" and "/linex.com/" in store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            if loc_dom.xpath('//h1[contains(text(), "COMING SOON")]'):
                location_type = "coming soon"

            hours_of_operation = loc_dom.xpath('//div[@class="hours-block"]/text()')

        location_name = loc_html.xpath(".//h4/text()")
        location_name = location_name[0] if location_name else "<MISSING"
        logger.info(f"Location Name: {location_name}")

        address_raw = loc_html.xpath(".//address/text()")
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if len(address_raw[0]) == 1:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip_code = "<MISSING>"
        else:
            street_address = address_raw[0]
            city = address_raw[-1].split(",")[0].split()[:-1]
            city = " ".join(city) if city else "<MISSING>"
            state = address_raw[-1].split(",")[0].split()[-1:]
            state = state[0] if state else "<MISSING>"
            zip_code = address_raw[-1].split(",")[-1].strip()
        country_code = "USA"
        if len(zip_code.split()) == 2:
            country_code = "CA"
        store_number = "<MISSING>"
        phone = loc_html.xpath(
            './/h5[contains(text(), "Contact:")]/following-sibling::p/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        hours_of_operation = loc_html.xpath('.//p[@class="hours"]/text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        if "coming soon" in location_name.lower() or street_address == "<MISSING>":
            continue
        logger.info(f"Hours of Operation: {hours_of_operation}")

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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    logger.info("Scraping started! ")
    data = fetch_data()
    logger.info(f"Number of items scraped and processed: {len(data)}")
    write_output(data)


if __name__ == "__main__":
    scrape()
