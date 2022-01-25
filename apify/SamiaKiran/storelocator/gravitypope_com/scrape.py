from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "gravitypope_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.gravitypope.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.gravitypope.com/pages/contact-us"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "grid__item large--one-quarter vcard"})[
            1:
        ]
        for loc in loclist:
            location_type = MISSING
            location_name = (
                loc.find("h4").get_text(separator="|", strip=True).replace("|", "")
            )
            if "general" in location_name:
                continue
            log.info(location_name)
            address = (
                loc.find("div", {"class": "location"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1] + " " + address[2]
            hours_of_operation = (
                loc.findAll("div", {"class": "hours"})[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if "Closed for the season" in hours_of_operation:
                hours_of_operation = MISSING
                location_type = "Temporarily Closed"
            try:
                phone = (
                    loc.find("div", {"class": "contact"})
                    .find("a")
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
            except:
                phone = MISSING
            country_code = "CA"
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
                location_type=location_type,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation.strip(),
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
