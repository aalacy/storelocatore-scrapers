from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "larsensrestaurants_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.larsensrestaurants.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.larsensrestaurants.com/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("window.POPMENU_APOLLO_STATE =")[1].split(
            '"CustomPageSelectedLocation'
        )[0]
        loclist = loclist.split('"RestaurantLocation:')[1:]
        for loc in loclist:
            store_number = loc.split('"id":')[1].split(",")[0]
            phone = loc.split('"displayPhone":"')[1].split('"')[0]
            street_address = loc.split('"streetAddress":"')[1].split('"')[0]
            city = loc.split('"city":"')[1].split('"')[0]
            country_code = loc.split('"country":"')[1].split('"')[0]
            state = loc.split('"state":"')[1].split('"')[0]
            zip_postal = loc.split('"postalCode":"')[1].split('"')[0]
            latitude = loc.split('"lat":')[1].split('"')[0]
            longitude = loc.split('"lng":')[1].split('"')[0]
            hours_of_operation = loc.split('"schemaHours":["')[1].split("]")[0]
            page_url = loc.split('"slug":"')[1].split('"')[0]
            page_url = "https://www.larsensrestaurants.com/" + page_url
            location_name = city + ", " + state
            zip_postal = zip_postal.split("-")[0]
            log.info(page_url)
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
