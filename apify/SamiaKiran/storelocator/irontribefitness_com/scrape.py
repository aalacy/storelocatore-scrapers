from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "irontribefitness_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}

DOMAIN = "https://irontribefitness.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://irontribefitness.com/Locations-Map"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split(" let detailLocations = [ ")[1].split(" ];")[0].split(" },")
        )
        for loc in loclist[:-1]:
            location_name = loc.split("name: '")[1].split("'")[0]
            log.info(location_name)
            store_number = loc.split("id: '")[1].split("'")[0]
            latitude = loc.split("lat: '")[1].split("'")[0]
            longitude = loc.split("lng: '")[1].split("'")[0]
            phone = loc.split("phone: '")[1].split("'")[0]
            street_address = loc.split("sA: '")[1].split("'")[0]
            city = loc.split("aL: '")[1].split("'")[0]
            state = loc.split("aR: '")[1].split("'")[0]
            zip_postal = loc.split("pC: '")[1].split("'")[0]
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
