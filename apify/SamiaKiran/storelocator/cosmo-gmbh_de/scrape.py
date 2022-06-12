import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import unidecode

session = SgRequests()
website = "cosmo-gmbh_de"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.cosmo-gmbh.de"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.cosmo-gmbh.de/standorte"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var locations = [")[1].split("];")[0].split("],")[:-1]
        for loc in loclist:
            loc = loc.replace("['", "")
            loc = BeautifulSoup(loc, "html.parser")
            location_name = strip_accents(
                loc.get_text(separator="|", strip=True).split("|")[0]
            )
            page_url = loc.findAll("a")[-1]["href"]
            if "beautyhairshop" in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll("div", {"class": "salons-two-column"})

            phone = MISSING
            hours_of_operation = strip_accents(
                temp[1].get_text(separator="|", strip=True).replace("|", " ")
            )

            hours_of_operation = hours_of_operation.split("Uhr")[0].strip()
            country_code = "DE"

            address_parts = (
                soup.find("div", attrs={"class": "content-gallery"})
                .find("div", attrs={"class": "left-content"})
                .find("p")
            )
            address_parts = str(address_parts).replace("<br/>", "")

            street_address = address_parts.split("\n")[1].strip()
            city_parts = (
                address_parts.split("\n")[-1].split("<")[0].strip().split(" ")[1:]
            )

            city = ""
            for part in city_parts:
                city = city + part + " "
            city = city[:-1].strip()

            state = "<MISSING>"
            zip_postal = (
                address_parts.split("\n")[-1]
                .split("<")[0]
                .strip()
                .split(" ")[0]
                .strip()
            )

            street_address = unidecode.unidecode(street_address)
            city = unidecode.unidecode(city)

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
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
