import re
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "laboiteapizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.laboiteapizza.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        r = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("select", {"name": "address"}).findAll("option")[1:]
        for loc in loclist:
            page_url = DOMAIN + loc["value"] + "restaurant"
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = strip_accents(
                    soup.find("p", {"class": "restaurant-title"})
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
                raw_address = strip_accents(
                    soup.find("p", {"class": "address_magasin"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                phone = (
                    soup.find("p", {"class": "tel"})
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
                hours_of_operation = (
                    soup.find("div", {"class": "opening"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                hours_of_operation = re.sub(pattern, "\n", hours_of_operation).replace(
                    "\n", " "
                )
                country_code = "FR"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
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
