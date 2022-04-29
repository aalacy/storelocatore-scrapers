import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome, SgSelenium
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "https://www.tacocabana.com"
logger = SgLogSetup().get_logger(logger_name="tacocabana_com")
MISSING = "<MISSING>"
locator_url = "https://www.tacocabana.com/find-a-tc-location/"


def get_hours_from_daily_schedule(url_location):
    driver = get_driver(url_location)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "showInfoModal")]'))
    )
    logger.info("[Store Information Loaded]")
    store_info_link = driver.find_element_by_xpath(
        '//a[contains(@href, "showInfoModal")]'
    )
    store_info_link.click()
    driver.implicitly_wait(20)
    logger.info("[Store Information Clicked]")
    driver.switch_to.active_element
    dropdown = driver.find_element_by_xpath("//div/h4/button")
    dropdown.click()
    driver.implicitly_wait(5)
    sel3 = html.fromstring(driver.page_source, "lxml")
    return sel3


def get_hours(url):
    temp_hours = []
    sel3 = get_hours_from_daily_schedule(url)
    scheduledays = sel3.xpath('//div[contains(@class, "_scheduleDay")]')
    for sch in scheduledays:
        days = sch.xpath(".//p/text()")
        days = " ".join(days)
        temp_hours.append(days)
        logger.info(days)
    return "; ".join(temp_hours)


def get_headers_for(url: str) -> dict:
    with SgChrome() as chrome:
        headers = SgSelenium.get_default_headers_for(chrome, url)
    return headers  # type: ignore


def get_driver(url, driver=None):
    driver = SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ).driver()
    driver.get(url)
    driver.implicitly_wait(3)
    return driver


def fetch_records(headers_):
    s = SgRequests(verify_ssl=False)
    r = s.get(locator_url, headers=headers_)
    sel = html.fromstring(r.text, "lxml")
    d = sel.xpath(
        '//script[contains(@type, text/javascript) and contains(text(), "var locations_meta")]/text()'
    )
    d1 = "".join(d)
    d2 = d1.split("var locations_meta = ")[-1]
    d3 = json.loads(d2)
    for idx1, i in enumerate(d3[0:]):
        j = i["map_pin"]
        page_url = i.get("order_now_link")

        location_name = j.get("name")
        logger.info(f"[{idx1}] [LOCNAME] {location_name}")

        # Street Address
        sta = ""
        streetnum = j.get("street_number")
        streetname = j.get("street_name")
        if streetnum and streetname:
            sta = streetnum + " " + streetname
        elif not streetnum and streetname:
            sta = streetname
        elif streetnum and not streetname:
            sta = streetnum
        else:
            sta = ""

        city = j.get("city")
        state = j.get("state_short")
        zip_postal = j.get("post_code")
        country_code = j.get("country_short")
        logger.info(f"[{idx1}] [CountryCode: {country_code}]")

        # Phone
        phone = ""
        if "map_pin_content" in i:
            map_content = i.get("map_pin_content")

            sel__phone = html.fromstring(map_content, "lxml")
            phone_raw = sel__phone.xpath("//text()")
            logger.info(phone_raw)
            pr = [" ".join(i.split()) for i in phone_raw]
            pr = [i for i in pr if i]
            phone = pr[-1]
        else:
            phone = ""
        store_number = j.get("place_id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = get_hours(page_url) or ""
        raw_address = j.get("address")
        item = SgRecord(
            locator_domain="tacocabana.com",
            page_url=page_url,
            location_name=location_name,
            street_address=sta,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
        yield item
        logger.info(f"[{idx1}] item: {item}")


def scrape():
    logger.info("Scraping Started")
    count = 0
    headers_ = get_headers_for(locator_url)

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_records(headers_)
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
