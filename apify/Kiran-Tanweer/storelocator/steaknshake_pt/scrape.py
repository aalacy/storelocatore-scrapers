from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup

session = SgRequests()
website = "steaknshake_pt"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://steaknshake.pt/"
MISSING = SgRecord.MISSING


def fetch_data():
    search_url = "https://steaknshake.pt/?lang=en"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc_block = soup.find("div", {"class": "row location"}).findAll(
        "div", {"class": "content"}
    )
    for loc in loc_block:
        title = loc.find("h3").text
        address = loc.findAll("p")[1].text
        details = address.split("\n")
        if len(details) == 3:
            street = details[0] + " " + details[1]
            phone = details[-1]
        else:
            street = details[0]
            phone = details[-1]
        street = street.rstrip(",").strip()
        hours = loc.findAll("tr")
        hoo = ""
        for hr in hours:
            hoo = hoo + " " + hr.text.replace("\n", " ")
        hoo = hoo.strip()
        hoo = hoo.replace("  ", " ")
        hoo = hoo.replace("Every day", "Mon-Sun")

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=DOMAIN,
            location_name=title,
            street_address=street.strip(),
            city=MISSING,
            state=MISSING,
            zip_postal=MISSING,
            country_code="PT",
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hoo.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
