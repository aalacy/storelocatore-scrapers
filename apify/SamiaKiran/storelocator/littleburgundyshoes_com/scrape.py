from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "littleburgundyshoes_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.littleburgundyshoes.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.littleburgundyshoes.com/stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "store panel-group"})
        for loc in loclist:
            location_name = loc.find("span", {"class": "storeName"}).text
            log.info(location_name)
            street_address = (
                loc.find("span", {"itemprop": "streetAddress"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            city = loc.find("span", {"itemprop": "addressLocality"}).text
            state = loc.find("span", {"itemprop": "addressRegion"}).text
            zip_postal = loc.find("span", {"itemprop": "postalCode"}).text
            country_code = loc.find("span", {"itemprop": "addressCountry"}).text
            phone = loc.find("span", {"itemprop": "telephone"}).text
            hours_of_operation = (
                soup.find("div", {"class": "hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
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
                location_type=MISSING,
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
