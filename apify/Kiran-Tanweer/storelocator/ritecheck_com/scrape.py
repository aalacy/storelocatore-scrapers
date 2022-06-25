from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "ritecheck_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://ritecheck.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        all_hour = []
        pattern = re.compile(r"\s\s+")
        cleanr = re.compile(r"<[^>]+>")
        search_url = "https://www.ritecheck.com/locations/"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        locations = soup.findAll(
            "h4", {"class": "elementor-heading-title elementor-size-default"}
        )
        hours = soup.findAll("ul", {"class": "elementor-icon-list-items"})
        i = 0
        for hr in hours:
            if i in range(5, 19):
                hour = hr.text
                hour = re.sub(pattern, " ", hour)
                hour = re.sub(cleanr, " ", hour)
                hour = hour.replace("\n", " ")
                all_hour.append(hour)
            i = i + 1

        for loc, hr in zip(locations, all_hour):
            address = loc.find("a").text
            address = re.sub(pattern, " ", address)
            address = re.sub(cleanr, " ", address)
            hour = hr.strip()
            address = address.replace("Open 24/7", "").strip()
            title = address

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.ritecheck.com/locations/",
                location_name=title,
                street_address=address.strip(),
                city=SgRecord.MISSING,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code=SgRecord.MISSING,
                store_number=SgRecord.MISSING,
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hour.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
