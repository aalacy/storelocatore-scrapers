from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "parkfast_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

DOMAIN = "https://www.parkfast.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://api.parkfast.com/locations/api/locations"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:

            page_url = "https://www.parkfast.com/location/" + loc["seoUrl"]
            location_name = MISSING
            log.info(page_url)
            store_number = loc["locationNumber"]
            phone = loc["phone1"]
            try:
                street_address = loc["address1"] + " " + loc["address2"]
            except:
                street_address = loc["address1"]
            city = loc["city"]
            state = MISSING
            zip_postal = loc["zip"]
            country_code = "US"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = loc["operatingHoursDescription"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.simplyfresh.info/find-a-store/",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
