from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape import sgpostal as parser
import re

session = SgRequests(verify_ssl=False)
website = "follain_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://follain.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://follain.com/pages/store-locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        locations = soup.findAll("div", {"class": "store-content"})
        for loc in locations:
            title = loc.find("h1").text
            address = loc.find("div", {"class": "store-address"}).text
            phone = loc.find(
                "div", {"class": "store-contact-text d-none d-md-block"}
            ).text
            phone = re.sub(pattern, " ", phone).strip()
            phone = phone.rstrip("beaconhill@follain.com").strip()
            address = re.sub(pattern, " ", address).strip()
            address = address.split("\n")[0].lstrip("Address").strip()
            parsed = parser.parse_address_usa(address)
            street1 = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            street = (
                (street1 + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else street1
            )
            city = parsed.city if parsed.city else "<MISSING>"
            state = parsed.state if parsed.state else "<MISSING>"
            pcode = parsed.postcode if parsed.postcode else "<MISSING>"

            hours = loc.find("div", {"class": "store-hours"}).text
            hours = re.sub(pattern, " ", hours).strip()
            hours = hours.lstrip("Hours").strip()

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=title.strip(),
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
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
