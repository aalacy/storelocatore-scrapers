from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "markettire_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://markettire.ca/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://markettire.ca/MyInstallers/data?enteredLocation=&isShowCommercialLocation=0"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = "https://markettire.ca" + loc["_href"]
            log.info(page_url)
            location_name = loc["company"]
            phone = loc["phone"]
            try:
                street_address = loc["address1"] + " " + loc["address2"]
            except:
                street_address = loc["address1"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = "CA"
            latitude = str(loc["latitude"])
            longitude = str(loc["longitude"])
            hours_of_operation = loc["hours"]
            store_number = loc["id"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
                hours_of_operation=hours_of_operation.strip(),
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
