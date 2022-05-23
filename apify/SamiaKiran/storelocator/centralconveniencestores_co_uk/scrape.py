import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "centralconveniencestores_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.centralconveniencestores.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.centralconveniencestores.co.uk/store-locator/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var map_locations =")[1].split("}];")[0] + "}]"
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = loc["col_name"]
            store_number = loc["col_id"]
            phone = MISSING
            street_address = loc["col_address1"]
            log.info(street_address)
            city = loc["col_city"]
            state = loc["col_state"]
            zip_postal = loc["col_postcode"]
            country_code = "GB"
            latitude = loc["col_latitude"]
            longitude = loc["col_longitude"]
            if "nan" in latitude:
                latitude = MISSING
                longitude = MISSING
            hours_of_operation = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
