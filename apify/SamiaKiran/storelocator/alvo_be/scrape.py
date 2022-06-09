import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "alvo_be"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.alvo.be"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.alvo.be/nl/winkels"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("table").findAll("tr")[1:]
        for loc in loclist:
            temp = loc.find("h2")
            page_url = DOMAIN + temp.find("a")["href"]
            location_name = temp.text
            log.info(page_url)
            street_address = strip_accents(
                loc.find("div", {"class": "thoroughfare"}).text
            )
            city = strip_accents(loc.find("span", {"class": "locality"}).text)
            zip_postal = loc.find("span", {"class": "postal-code"}).text
            state = MISSING
            country_code = strip_accents(
                loc.find("span", {"class": "country"}).text.replace("«", "")
            )
            phone = loc.find("span", {"class": "phone-number"}).text
            hours_of_operation = (
                loc.find("div", {"class": "field-shop-hours-opening"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
