from lxml import etree
from time import sleep
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
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
MAX_WORKERS = 5
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(10))
def fetch_all_locs(zipcode):
    start_url = "https://linex.com/find-a-location"
    try:
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

            logger.info(f"Pulling the search results for the zipcode: {zipcode}")
            driver.find_element_by_xpath('//input[@name="location"]').send_keys(zipcode)
            sleep(2)
            logger.info("zipcode - send_keys executed")
            driver.find_element_by_xpath('//button[contains(text(), "Search")]').click()
            sleep(20)
            logger.info("Search Button Clicked")
            driver.find_element_by_xpath('//input[@name="location"]').clear()
            code_dom = etree.HTML(driver.page_source)
            all_locations = code_dom.xpath('//div[@class="find-result "]')
            return all_locations
    except Exception as e:
        raise Exception(
            f"Please fix SgSeleniumError <<{e}>> for the search zipcode of {zipcode}"
        )


def fetch_data(all_locs):
    # Your scraper here
    all_locations_list = list(set(all_locs))
    logger.info(f"all locations raw:\n {all_locations_list}")
    logger.info(f"Total Store Count: {len(all_locations_list)}")
    s = set()
    for idx, loc_html in enumerate(all_locations_list[0:]):
        page_url = loc_html.xpath('.//a[contains(text(), "Visit Website")]/@href')
        page_url = "".join(page_url).replace(" ", "").replace("http://https", "https")

        if page_url in s:
            continue
        else:
            s.add(page_url)
            page_url = "".join(page_url.split())
            page_url = page_url if page_url else MISSING
            if "https://linex.com/us/line-x-of-venice-F1379" in page_url:
                continue
            logger.info(f"[{idx}] Page URL: {page_url}")

            # Location Name
            location_name = "".join(loc_html.xpath("./@data-title"))
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] Location Name: {location_name}")

            location_name_csoon = "".join(loc_html.xpath(".//h4//text()"))
            location_name_csoon = " ".join(location_name_csoon.split())
            logger.info(f"[{idx}] Location Name Coming Soon: {location_name_csoon}")

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

            store_number = None
            if "-" in page_url:
                store_number = page_url.split("-")[-1]
            else:
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
            hoo = loc_html.xpath('.//p[@class="hours"]/text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else MISSING
            if "coming soon" in location_name_csoon.lower():
                hours_of_operation = "Coming Soon"
            logger.info(f"[{idx}] Hours of Operation: {hours_of_operation}")
            raw_address = MISSING
            rec = SgRecord(
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
            yield rec


def get_all_raw_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=200,
    )

    all_locations = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [executor.submit(fetch_all_locs, szipcode) for szipcode in search]
        tasks.extend(task)
        for future in as_completed(tasks):
            res = future.result()
            all_locations.extend(res)
    return all_locations


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
        all_locs_data = get_all_raw_data()
        results = fetch_data(all_locs_data)
        for rec in results:
            if rec is not None:
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
