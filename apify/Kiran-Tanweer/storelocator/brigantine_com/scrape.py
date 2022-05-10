from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
import re
from sgscrape import sgpostal as parser


session = SgRequests()
website = "brigantine_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.brigantine.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    search_url = "https://www.brigantine.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc_block = soup.find("div", {"id": "locations-list"}).findAll(
        "div", {"class": "location-item"}
    )
    for store in loc_block:
        link = store["data-link"]
        stores_req = session.get(link, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        title = (
            soup.find("section", {"class": "location-heading"}).find("h2").text.strip()
        )
        title = re.sub(pattern, " ", title)
        title = re.sub(cleanr, " ", title)
        address = soup.find("div", {"class": "address"}).text.strip()
        phone = soup.find("div", {"class": "phone"}).text.strip()
        hours = soup.find("div", {"class": "hours _display-desktop"}).text.strip()
        hours = re.sub(pattern, " ", hours)
        hours = re.sub(cleanr, " ", hours)
        phone = phone.split("\n")[1].strip()
        hours = hours.replace("View Menus", "").strip()
        hours = hours.replace("Hours ", "").strip()
        address = re.sub(pattern, " ", address)
        address = re.sub(cleanr, " ", address)
        address = address.replace("Address ", "").strip()

        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code="US",
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours.strip(),
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
