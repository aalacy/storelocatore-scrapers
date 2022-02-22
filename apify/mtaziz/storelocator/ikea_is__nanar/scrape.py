from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt
import tenacity
from lxml import html
import time
import json
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


LOCATION_URL = "https://www.ikea.is/nanar"
DOMAIN = "ikea.is"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("ikea_is__nanar")

headers = {
    "accept": "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "MMozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
)


def get_driver(url, class_name, timeout, driver=None):
    if driver is not None:
        driver.quit()
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 6:
                raise Exception("Fix the issue:(")
            return
    return driver


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(urlnum, url):
    with SgRequests() as http:
        logger.info(f"[{urlnum}] Pulling the data from: {url}")
        r = http.get(url, headers=headers)
        if r.status_code == 200:
            logger.info(f"HTTP Status Code: {r.status_code}")
            return r
        raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def get_googlemap_place_details_urls():
    class_name = "container-fluid"
    driver = get_driver(LOCATION_URL, class_name, 30)
    iframe_xpath = '//iframe[contains(@src, "google.com/maps/d/embed?mid=")]'
    iframe = driver.find_element_by_xpath(iframe_xpath)
    driver.switch_to.frame(iframe)
    logger.info("Switch to iframe")
    selg = html.fromstring(driver.page_source)
    gmap_url = selg.xpath('//meta[@itemprop="url"]/@content')[0]
    logger.info(f"Google Map URL: {gmap_url}")
    driver2 = get_driver(gmap_url, "i4ewOd-haAclf", 30)
    place_details_url_list = []
    time.sleep(10)
    s1 = set()
    for i in range(0, 3):
        driver2.find_element_by_xpath(
            f'//div[@role="button" and contains(@style, "z-index: {str(i)};")]/img'
        ).click()
        time.sleep(10)
        sel = html.fromstring(driver2.page_source)
        getplacedetails_xpath = (
            '//script[contains(@src, "PlaceService.GetPlaceDetails")]/@src'
        )
        getplacedetails_url = sel.xpath(getplacedetails_xpath)
        logger.info(f"place details url: {getplacedetails_url}")
        locname_xpath = '//div[contains(text(), "name")]/following-sibling::div/text()'
        ln = "".join(sel.xpath(locname_xpath))
        for gpd in getplacedetails_url:
            if gpd not in s1:
                place_details_url_list.append((gpd, ln))
            s1.add(gpd)

        logger.info(f"place details url: {getplacedetails_url}")
    return place_details_url_list


def fetch_data():
    ggmap_url_list = get_googlemap_place_details_urls()

    for idx, gurl in enumerate(ggmap_url_list[0:]):
        locator_domain = DOMAIN
        page_url = LOCATION_URL

        # We need to transform the data into JSON format
        r1 = get_response(idx, gurl[0])

        data_raw1 = "{" + r1.text.split("( {")[-1]
        data_raw2 = data_raw1.lstrip().rstrip(")").split()
        data_raw2 = " ".join(data_raw2)
        data_json = json.loads(data_raw2)
        result_address = data_json["result"]["adr_address"]
        location_name = gurl[1]
        location_name = location_name if location_name else MISSING
        logger.info(f"[{idx}] Location Name: {location_name}")

        # Parse JSON data
        sel_result_address = html.fromstring(result_address, "lxml")
        street_address = sel_result_address.xpath(
            '//span[@class="street-address"]/text()'
        )
        street_address = "".join(street_address)
        street_address = street_address if street_address else MISSING
        logger.info(f"[{idx}] Street Address: {street_address}")

        city = sel_result_address.xpath('//span[@class="locality"]/text()')
        city = "".join(city)
        city = city if city else MISSING
        logger.info(f"[{idx}] City: {city}")

        state = sel_result_address.xpath('//span[@class="region"]/text()')
        state = "".join(state)
        state = state if state else MISSING
        logger.info(f"[{idx}] Location Name: {location_name}")

        zip_postal = sel_result_address.xpath('//span[@class="postal-code"]/text()')
        zip_postal = "".join(zip_postal)
        zip_postal = zip_postal if zip_postal else MISSING
        logger.info(f"[{idx}] Zip Postal: {zip_postal}")

        country_code = sel_result_address.xpath('//span[@class="country-name"]/text()')
        country_code = "".join(country_code)
        country_code = country_code if country_code else MISSING
        logger.info(f"[{idx}] country_code: {country_code}")

        store_number = MISSING
        try:
            if "international_phone_number" in data_json["result"]:
                phone = data_json["result"]["international_phone_number"]
                phone = phone if phone else MISSING

        except:
            phone = MISSING
        logger.info(f"[{idx}] Phone: {phone}")

        location_type = MISSING

        latitude = data_json["result"]["geometry"]["location"]["lat"]
        latitude = latitude if latitude else MISSING
        logger.info(f"[{idx}] latitude: {latitude}")

        longitude = data_json["result"]["geometry"]["location"]["lng"]
        longitude = longitude if longitude else MISSING
        logger.info(f"[{idx}] longitude: {longitude}")
        hours_of_operation = ""
        try:
            if "opening_hours" in data_json["result"]:
                hours = data_json["result"]["opening_hours"]["weekday_text"]
                if hours:
                    hours_of_operation = "; ".join(hours)
                else:
                    hours_of_operation = MISSING
        except:
            hours_of_operation = MISSING

        raw_address = data_json["result"]["formatted_address"]
        raw_address = raw_address if raw_address else MISSING
        logger.info(f"[{idx}] raw_address: {raw_address}")

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
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
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
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
