from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "firstrust_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.firstrust.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.firstrust.com/#locations-menu"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div", {"class": "location-card card d-flex flex-column"}
        )
        for loc in loclist:
            try:
                page_url = loc.find(
                    "a",
                    {"class": "cta locations-schedule-appointment d-flex w-100 mb-3"},
                )["href"]
            except:
                page_url = url
            if DOMAIN not in page_url:
                page_url = DOMAIN + page_url
            log.info(page_url)
            location_name = loc["data-name"]
            latitude = loc["data-lat"]
            longitude = loc["data-lng"]
            city = loc["data-city"]
            state = loc["data-state"]
            zip_postal = loc["data-postal"]
            try:
                street_address = (
                    loc.find("p", {"class": "location-addr"}).text
                    + " "
                    + loc.find("p", {"class": "location-addr-two"}).text
                )
            except:
                street_address = loc.find("p", {"class": "location-addr"}).text
            phone = loc.find("a", {"class": "location-phone"}).text
            hours_of_operation = (
                loc.find("p", {"class": "location-hour"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if hours_of_operation == ".":
                hours_of_operation = MISSING
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
