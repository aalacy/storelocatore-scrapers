import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rexel_fi"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://rexel.fi/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.rexel.fi/cms/ajax.html?block=9"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "contact-item js-search-results"})
        coord_url = "https://www.rexel.fi/yhteystiedot.html"
        r = session.get(coord_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        coord_list = soup.findAll("div", {"class": "js-singleLocation"})
        for loc in loclist:
            city = strip_accents(loc.find("span", {"class": "contact-item-city"}).text)
            phone = loc.find("span", {"class": "contact-item-phone"}).text
            log.info(phone)
            for coord in coord_list:
                if city == coord["data-town"]:
                    coords = coord["data-coordinates"].split(",")
                    latitude = coords[0]
                    longitude = coords[1]
            country_code = "FI"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=coord_url,
                location_name=MISSING,
                street_address=MISSING,
                city=city.strip(),
                state=MISSING,
                zip_postal=MISSING,
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
