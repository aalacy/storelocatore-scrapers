from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html
from tenacity import retry, stop_after_attempt
import tenacity
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

session = SgRequests()

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

logger = SgLogSetup().get_logger("ballarddesigns_com")
MISSING = SgRecord.MISSING


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(15))
def get_response_hours(driver, page_url):
    driver.get(page_url)
    sel = html.fromstring(driver.page_source)
    hours_raw = sel.xpath('//div[contains(@id, "store-hours")]//text()')
    logger.info(f"Raw Hours: {hours_raw}")  # noqa
    hoo = ""
    hours = [" ".join(i.split()) for i in hours_raw]
    hours = [" ".join(i.split()) for i in hours if i]
    if hours:
        try:
            if hours:
                hoo = "; ".join(hours)
            else:
                hoo = MISSING
        except Exception as e:
            hoo = MISSING
            logger.info(f"HoursOfOperationError Ignored! << {e} >> at {hours}")  # noqa
        return hoo
    else:
        raise Exception(
            f"Please Fix HoursOfOperationError or HttpCodeError: {page_url} | {hours_raw}"
        )


def fetch_data(driver):
    url = "https://www.ballarddesigns.com/wcsstore/images/BallardDesigns/_media/locations/store-location-info.json"
    r = session.get(url, headers=headers)
    data = r.json()
    store_info = data["storeInfo"]
    count = 0
    for k, v in store_info.items():
        page_url = "https://www.ballarddesigns.com" + v["storePageURL"]
        sta = ""
        try:
            sta1 = v["address1"]
            sta2 = v["address2"]
            if sta1 and sta2:
                sta = sta1 + ", " + sta2
            elif sta1 and not sta2:
                sta = sta1
            elif not sta1 and sta2:
                sta = sta2
            elif not sta1 and not sta2:
                sta = MISSING
            else:
                sta = MISSING
        except Exception as e:
            sta = MISSING
            logger.info(f"Fix StreetAddressError: << {e} >> at {v}")

        count += 1
        logger.info(f"Pulling the hours info from {page_url}")  # noqa
        hours_oo = get_response_hours(driver, page_url)
        logger.info(f"HoursOfOperation: {hours_oo} for {page_url}")  # noqa

        item = SgRecord(
            locator_domain="ballarddesigns.com",
            page_url=page_url,
            location_name=v["storeName"],
            street_address=sta,
            city=v["city"] or MISSING,
            state=v["stateAbbr"] or MISSING,
            zip_postal=v["zipCode"],
            country_code="US",
            phone=v["telephone"],
            location_type=MISSING,
            store_number=MISSING,
            latitude=v["geo"]["latitude"] or MISSING,
            longitude=v["geo"]["longitude"] or MISSING,
            hours_of_operation=hours_oo,
        )
        yield item
    logger.info(f"Total Store Count: {count}")


def scrape(driver):
    results = fetch_data(driver)
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


if __name__ == "__main__":
    logger.info("Scrape Started")  # noqa
    with SgChrome(
        is_headless=True, executable_path=ChromeDriverManager().install()
    ) as driver:
        scrape(driver)
    logger.info("Scrape Finished!")  # noqa
