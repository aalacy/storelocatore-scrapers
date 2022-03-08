import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "spar_sa"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://spar.sa/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://spar.sa/Branches"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var markers = ")[1].split("}];")[0]
        loclist = json.loads(loclist.replace("'", '"') + "}]")
        for loc in loclist:
            location_name = loc["title"]
            log.info(location_name)
            street_address = location_name
            latitude = loc["lat"]
            longitude = loc["lng"]
            country_code = "SA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=MISSING,
                state=MISSING,
                zip_postal=MISSING,
                country_code=country_code,
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
