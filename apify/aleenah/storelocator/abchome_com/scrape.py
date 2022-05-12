from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
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
    url = "https://abchome.com/pages/contact"
    res = session.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    loclist = soup.findAll("div", {"class": "tt-contact02-col-list"})[1].findAll(
        "div", {"class": "col-md"}
    )
    for loc in loclist:
        location_name = loc.find("h6").text
        log.info(location_name)
        phone = MISSING
        address = loc.find("address").get_text(separator="|", strip=True).split("|")
        hours_of_operation = address[-2] + " " + address[-1]
        street_address = address[0]
        address = address[1].split(",")
        city = address[0]
        address = address[1].split()
        state = address[0]
        zip_postal = address[1]
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
