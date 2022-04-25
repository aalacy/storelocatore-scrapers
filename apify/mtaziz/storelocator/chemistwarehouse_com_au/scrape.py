from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import cloudscraper
import os
from tenacity import retry, stop_after_attempt
import tenacity


logger = SgLogSetup().get_logger(logger_name="chemistwarehouse_com_au")
DOMAIN = "chemistwarehouse.com.au"
STORE_LOCATOR = "https://www.chemistwarehouse.com.au/aboutus/store-locator"
proxy_password = os.environ["PROXY_PASSWORD"]
DEFAULT_PROXY_URL = (
    f"http://groups-RESIDENTIAL,country-us:{proxy_password}@proxy.apify.com:8000/"
)
proxies = {
    "http": DEFAULT_PROXY_URL,
    "https": DEFAULT_PROXY_URL,
}  # Proxy that works with cloudscraper


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(url):
    scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
    scraper.proxies = proxies
    stores_req = scraper.get(url)
    logger.info(
        "<=========================START OF RESPONSECONTNT=========================>"
    )

    logger.info(
        f"HTTPSTATUS: {stores_req.status_code} | ResponseContent: {stores_req.text}"
    )
    logger.info(
        "<=========================END OF RESPONSECONTNT=========================>"
    )
    if stores_req.status_code == 200:
        logger.info(f"[ {url} ]")
        logger.info(f"{url} >> HTTP Status: {stores_req.status_code}")
        return stores_req

    raise Exception(f"{url} >> TemporaryError: {stores_req.status_code}")


def fetch_data():
    search_url = "https://www.chemistwarehouse.com.au/ams/webparts/Google_Map_SL_files/storelocator_data.ashx?searchedPoint=(-35.1423355,%20149.0353134)"
    stores_req = get_response(search_url)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    markers = soup.findAll("marker")
    for _ in markers:
        mon = _["storemon"]
        tue = _["storetue"]
        wed = _["storewed"]
        thu = _["storethu"]
        fri = _["storefri"]
        sat = _["storesat"]
        sun = _["storesun"]
        hours = f"Mon {mon}; Tue {tue}; Wed {wed}; Thu {thu}; Fri {fri}; Sat {sat}; Sun {sun}"
        hours = hours.strip()
        item = SgRecord(
            locator_domain=DOMAIN,
            page_url=STORE_LOCATOR,
            location_name=_["storename"],
            street_address=_["storeaddress"],
            city=_["storesuburb"].strip(),
            state=_["storestate"].strip(),
            zip_postal=_["storepostcode"].strip(),
            country_code="AU",
            store_number=_["id"],
            phone=_["storephone"],
            location_type="",
            latitude=_["lat"],
            longitude=_["lng"],
            hours_of_operation=hours,
        )
        yield item


def scrape():
    logger.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
