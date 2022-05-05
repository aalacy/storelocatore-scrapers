from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "brigantine_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "http://www.brigantine.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        stores_req = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        locations = soup.find("div", {"class": "section-body grid clearfix"})
        loclist = locations.findAll("div", {"class": "location"})
        for loc in loclist:
            location_name = loc.find("h3", {"itemprop": "name"}).text
            log.info(location_name)
            phone = loc.find("p", {"class": "location-phone"}).text
            street = loc.find("span", {"itemprop": "streetAddress"}).text
            city = loc.find("span", {"itemprop": "addressLocality"}).text
            state = loc.find("span", {"itemprop": "addressRegion"}).text
            pcode = loc.find("span", {"itemprop": "postalCode"}).text
            pcode = pcode.rstrip("Click here to book a private event")
            pcode = pcode.rstrip("CLICK HERE TO BOOK A PRIVATE EVENT")
            hours = loc.find("div", {"class": "list-location"}).text
            hours = hours.replace("\n", " ").strip()
            hours = hours.lstrip("BRIG-207-KETCH-BREWING_KM_MENU")
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=DOMAIN,
                location_name=location_name,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours,
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
