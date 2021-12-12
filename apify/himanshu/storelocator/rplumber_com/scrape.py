from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rplumber_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers={
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.rplumber.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://api.rplumber.com/locations"
        loclist= session.get(url, headers=headers).json()['data']
        for loc in loclist:
            location_name = loc['name']
            if location_name is None:
                location_name  = "<INACCESSIBLE>"
            store_number = loc["id"]
            phone = loc["phone"]
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            log.info(street_address)
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = "US"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = str(loc['hours']).replace("', '"," ").replace("': '"," ").replace("{'","").replace("'}","")
            if 'None' in hours_of_operation:
                hours_of_operation = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.rplumber.com/locations",
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
