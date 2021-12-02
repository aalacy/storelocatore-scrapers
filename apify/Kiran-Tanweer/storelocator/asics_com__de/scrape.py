from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import os


os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"


session = SgRequests()
website = "asics_com__de"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.asics.com/",
    "Origin": "https://www.asics.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}


DOMAIN = "https://www.asics.com/de"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://cdn.crobox.io/content/ujf067/229/stores.json"
        req = session.get(search_url, headers=headers).json()
        for store in req:
            street = store["address"]
            city = store["city"]
            lat = store["lat"]
            lng = store["lng"]
            title = store["name"]
            phone = store["phone"]
            pcode = store["postalCode"]
            store_type = store["storetype"]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=DOMAIN,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=MISSING,
                zip_postal=pcode,
                country_code=MISSING,
                store_number=MISSING,
                phone=phone,
                location_type=store_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS})
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
