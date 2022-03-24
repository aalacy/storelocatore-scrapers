import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "fraserhart_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://fraserhart.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.fraserhart.co.uk/aw_store_locator"
        r = session.get(url, headers=headers)
        loclist = json.loads(r.text.split(' "locationItems": ')[1].split("]")[0] + "]")
        for loc in loclist:
            page_url = "https://www.fraserhart.co.uk/store/" + loc["url_key"]
            log.info(page_url)
            location_name = loc["title"]
            store_number = loc["location_id"]
            phone = loc["phone"]
            street_address = loc["street"]
            log.info(street_address)
            city = loc["city"]
            state = MISSING
            zip_postal = loc["zip"]
            country_code = loc["country_id"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = loc["openings"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = hours_of_operation.get_text(
                separator="|", strip=True
            ).replace("|", " ")
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
