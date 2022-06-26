import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "snipes.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.snipes.com"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text)


def fetch_data():
    if True:
        url = "https://www.snipes.com/on/demandware.store/Sites-snse-SOUTH-Site/de_DE/Stores-FindStores?lat=0&long=0&radius=10000000"
        r = session.get(url, headers=headers)
        loclist = r.text.replace("\n", "")
        loclist = json.loads(loclist)["stores"]
        for loc in loclist:
            page_url = DOMAIN + loc["url"]
            log.info(page_url)
            location_name = strip_accents(loc["name"])
            store_number = loc["ID"]
            try:
                phone = loc["phone"]
            except:
                phone = MISSING
            try:
                street_address = loc["address1"] + " " + loc["address2"]
            except:
                street_address = loc["address1"]
            street_address = strip_accents(street_address)
            city = strip_accents(loc["city"])
            state = MISSING
            zip_postal = loc["postalCode"]
            country_code = loc["countryCode"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = strip_accents(loc["storeHours"])
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
