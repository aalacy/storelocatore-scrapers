from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "godfatherspizza_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://godfatherspizza.ca"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://godfatherspizza.ca/locations/"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split("Over 25 locations throughout Ontario, Canada.")[1]
            .split("<footer")[0]
            .split("Order Online")[:-1]
        )
        for loc in loclist:
            loc = (
                BeautifulSoup(loc, "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            location_name = loc[0]
            log.info(location_name)
            street_address = loc[1]
            city = MISSING
            state = "Ontario"
            zip_postal = MISSING
            country_code = "CA"
            phone = loc[-1]
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
                latitude=MISSING,
                longitude=MISSING,
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
