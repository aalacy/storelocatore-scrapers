from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup

session = SgRequests()
website = "chemistwarehouse_co_nz"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://chemistwarehouse.com.nz/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.chemistwarehouse.co.nz/ams/webparts/Google_Map_SL_files/storelocator_data.ashx?searchedPoint=(-43.9979593,%20173.0361376)"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        markers = soup.findAll("marker")
        for store in markers:
            title = store["storename"]
            storeid = store["id"]
            lat = store["lat"]
            lng = store["lng"]
            hours = (
                "Mon "
                + store["storemon"]
                + " tues "
                + store["storetue"]
                + " wed "
                + store["storewed"]
                + " thurs "
                + store["storethu"]
                + " fri "
                + store["storefri"]
                + " sat "
                + store["storesat"]
                + " Sun "
                + store["storesun"]
            )
            street = store["storeaddress"]
            phone = store["storephone"]
            pcode = store["storepostcode"]
            state = store["storestate"]
            city = store["storesuburb"]
            hours = hours.strip()

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=DOMAIN,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="NZ",
                store_number=storeid,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
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
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
