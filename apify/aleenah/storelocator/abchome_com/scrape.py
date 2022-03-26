from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "abchome_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://abchome.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    res = session.get(DOMAIN)
    soup = BeautifulSoup(res.text, "html.parser")
    loclist = soup.find_all("div", {"class": "container-2 w-container"})[:-1]
    for loc in loclist:
        location_name = loc.find("h2").text
        log.info(location_name)
        phone = loc.select_one("a[href*=tel]").text
        temp = loc.findAll("p", {"class": "hero-subheading"})
        address = temp[0].get_text(separator="|", strip=True).split("|")
        street_address = address[0]
        address = address[1].split(",")
        city = address[0]
        address = address[1].split()
        state = address[0]
        zip_postal = address[1]
        hours_of_operation = (
            temp[1]
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("Hours", "")
        )
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=DOMAIN,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours_of_operation,
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
