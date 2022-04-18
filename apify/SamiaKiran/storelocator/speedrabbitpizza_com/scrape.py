import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "speedrabbitpizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.speedrabbitpizza.com"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.speedrabbitpizza.com/le_plus_proche/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "shop_details"})
        for loc in loclist:
            location_name = strip_accents(
                loc.find("h5", {"itemprop": "name"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            log.info(location_name)
            phone = (
                loc.find("p", {"itemprop": "telephone"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            street_address = strip_accents(
                loc.find("p", {"itemprop": "streetAddress"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            city = strip_accents(
                loc.find("span", {"itemprop": "addressLocality"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            state = MISSING
            zip_postal = (
                loc.find("span", {"itemprop": "postalCode"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            hours_of_operation = strip_accents(
                loc.text.split("Horaires d'ouverture:")[1]
                .split("Choisir ce magasin")[0]
                .replace("\n", " ")
            )
            country_code = "FR"
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
