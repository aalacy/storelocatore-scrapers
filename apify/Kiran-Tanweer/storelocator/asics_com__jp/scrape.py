from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


session = SgRequests()
website = "asics_com__jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

DOMAIN = "https://www.asics.com/jp"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.asics.com/jp/ja-jp/store-locator.json?per-page=2000"
        response = session._session.get(search_url, timeout=1000)
        req = response.json()
        for store in req["Stores"]:
            loc = req["Stores"][store]
            storeid = loc["ID"]
            title = loc["Title"]
            street = loc["Address"]
            city = loc["City"]
            region = loc["Region"]
            pcode = loc["Postcode"]
            phone = loc["Phone"]
            lat = loc["Latitude"]
            lng = loc["Longitude"]
            url = "https://www.asics.com" + loc["URL"]
            loc_type = loc["StoreType"]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=region.strip(),
                zip_postal=pcode,
                country_code="JP",
                store_number=storeid,
                phone=phone,
                location_type=loc_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
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
