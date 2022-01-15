from lxml import etree
from time import sleep
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sgselenium import SgChrome
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.sgrecord_id import SgRecordID

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("linex_com")
DOMAIN = "linex.com"
MISSING = SgRecord.MISSING


def fetch_data():
    # Your scraper here
    session = SgRequests()

    start_url = "https://linex.com/find-a-location"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
        max_search_results=None,
    )

    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        driver.get(start_url)
        sleep(5)
        driver.find_element_by_xpath(
            '//span[contains(text(), "International") or contains(text(), "United States") or contains(text(), "Canada")]'
        ).click()
        sleep(5)
        logger.info("International Clicked")
        driver.find_element_by_xpath(
            '//span[contains(text(), "United States")]'
        ).click()
        logger.info("United States Clicked")
        for code in all_codes:
            logger.info(f"Pulling the search results for the zipcode: {code}")
            driver.find_element_by_xpath('//input[@name="location"]').send_keys(code)
            sleep(2)
            logger.info("zipcode - send_keys executed")
            driver.find_element_by_xpath('//button[contains(text(), "Search")]').click()
            sleep(20)
            logger.info("Search Button Clicked")
            driver.find_element_by_xpath('//input[@name="location"]').clear()

            code_dom = etree.HTML(driver.page_source)
            all_locations += code_dom.xpath('//div[@class="find-result "]')
    all_locations_list = list(set(all_locations))
    for idx, loc_html in enumerate(all_locations_list[0:]):

        page_url = loc_html.xpath('.//a[contains(text(), "Visit Website")]/@href')
        page_url = "".join(page_url).replace(" ", "").replace("http://https", "https")
        page_url = "".join(page_url.split())
        page_url = page_url if page_url else MISSING
        logger.info(f"[{idx}] Page URL: {page_url}")

        # Location Name
        location_name = "".join(loc_html.xpath(".//h4/text()"))
        location_name = " ".join(location_name.split())
        location_name = location_name if location_name else "<MISSING"
        logger.info(f"[{idx}] Location Name: {location_name}")

        address_raw = loc_html.xpath(".//address/text()")
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if len(address_raw[0]) == 1:
            street_address = MISSING
            city = MISSING
            state = MISSING
            zip_code = MISSING
        else:
            street_address = address_raw[0]
            city = address_raw[-1].split(",")[0].split()[:-1]
            city = " ".join(city) if city else MISSING
            state = address_raw[-1].split(",")[0].split()[-1:]
            state = state[0] if state else MISSING
            zip_code = address_raw[-1].split(",")[-1].strip()
        country_code = "US"
        if len(zip_code.split()) == 2:
            country_code = "CA"
        store_number = MISSING
        phone = loc_html.xpath(
            './/h5[contains(text(), "Contact:")]/following-sibling::p/text()'
        )
        phone = phone[0] if phone else MISSING
        logger.info(f"[{idx}] Phone: {phone}")

        # Latlng
        latitude = "".join(loc_html.xpath("./@data-lat"))
        latitude = latitude if latitude else MISSING
        logger.info(f"[{idx}] Latitude: {latitude}")

        longitude = "".join(loc_html.xpath("./@data-lon"))
        longitude = longitude if longitude else MISSING
        logger.info(f"[{idx}] Longitude: {longitude}")

        location_type = MISSING
        hours_of_operation = ""

        if page_url != MISSING and "/linex.com/" in page_url:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            if loc_dom.xpath('//h1[contains(text(), "COMING SOON")]'):
                location_type = "Coming Soon"

            hours_of_operation = loc_dom.xpath('//div[@class="hours-block"]/text()')

        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else MISSING
        )

        hours_of_operation = loc_html.xpath('.//p[@class="hours"]/text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else MISSING
        )

        if "coming soon" in location_name.lower() or street_address == MISSING:
            continue
        logger.info(f"[{idx}] Hours of Operation: {hours_of_operation}")
        raw_address = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
