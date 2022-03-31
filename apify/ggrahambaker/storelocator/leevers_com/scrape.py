from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "leevers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.leevers.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        loclist = r.text.split("Save-A-Lot")[1:-1]
        for loc in loclist:
            location_name = "Save-A-Lot"
            loc = (
                BeautifulSoup(loc, "html.parser")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = loc[0]
            log.info(street_address)
            address = loc[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            phone = loc[2].replace("PH:", "")
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
                hours_of_operation=MISSING,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
