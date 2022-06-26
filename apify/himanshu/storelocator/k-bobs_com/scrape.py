from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "k-bobs.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.k-bobs.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:

        url = "https://www.k-bobs.com/locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<h6 class="fw-special-title">')[1:]
        for loc in loclist:
            loc = '<h6 class="fw-special-title">' + loc
            soup = BeautifulSoup(loc, "html.parser")
            location_name = soup.find("h6").text
            log.info(location_name)
            temp = soup.findAll("div", {"class": "fw-text-inner"})
            address = temp[0].get_text(separator="|", strip=True).split("|")
            if "Temporarily Closed" in address[0]:
                location_type = "Temporarily Closed"
                address = address[1:]
            phone = address[-1]
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            location_type = MISSING
            hours_of_operation = temp[1]
            if "JOIN THE WAITLIST" in hours_of_operation.text:
                hours_of_operation = temp[2]
            hours_of_operation = (
                hours_of_operation.find("p")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=location_type,
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
