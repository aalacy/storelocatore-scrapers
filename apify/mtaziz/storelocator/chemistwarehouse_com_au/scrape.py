from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import cloudscraper


logger = SgLogSetup().get_logger(logger_name="chemistwarehouse_com_au")
DOMAIN = "chemistwarehouse.com.au"
STORE_LOCATOR = "https://www.chemistwarehouse.com.au/aboutus/store-locator"


def fetch_data():
    search_url = "https://www.chemistwarehouse.com.au/ams/webparts/Google_Map_SL_files/storelocator_data.ashx?searchedPoint=(-35.1423355,%20149.0353134)"
    scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
    stores_req = scraper.get(search_url)
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
    with SgRequests() as http:
        r = http.get(STORE_LOCATOR)
        logger.info(f"HttpStatusCode: {r.status_code}")
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
