import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "redcarpetcarwash_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.redcarpetcarwash.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.redcarpetcarwash.com/full-service"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "col sqs-col-4 span-4"})
        for loc in loclist:
            temp = loc.find(
                "div", {"class": "sqs-block map-block sqs-block-map sized vsize-12"}
            )["data-block-json"]
            temp = json.loads(temp)
            temp = temp["location"]
            latitude = temp["mapLat"]
            longitude = temp["mapLng"]
            street_address = temp["addressLine1"]
            log.info(street_address)
            address = temp["addressLine2"]
            address = address.split(",")
            city = address[0]
            state = address[1]
            zip_postal = address[2]
            country_code = temp["addressCountry"]
            temp = loc.find("p").get_text(separator="|", strip=True).split("|")
            location_name = MISSING
            hours_of_operation = temp[1] + " " + temp[2]
            phone = temp[3]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
