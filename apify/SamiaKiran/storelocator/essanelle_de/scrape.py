import html
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "essanelle_de"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.essanelle.de"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.essanelle.de/wp-content/plugins/store-locator/sl-xml.php"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("marker")
        for loc in loclist:
            location_name = strip_accents(loc["name"])
            phone = loc["phone"]
            try:
                street_address = loc["street"] + " " + loc["street2"]
            except:
                street_address = loc["street"]
            street_address = html.unescape(strip_accents(street_address))
            log.info(location_name)
            city = strip_accents(loc["city"])
            state = strip_accents(loc["state"])
            zip_postal = loc["zip"]
            country_code = "DE"
            latitude = loc["lat"]
            longitude = loc["lng"]
            hours_of_operation = html.unescape(loc["hours"])
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.essanelle.de/salonfinder/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
