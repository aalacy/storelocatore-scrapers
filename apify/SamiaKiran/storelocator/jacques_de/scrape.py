import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "jacques.de"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.jacques.de"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        state = MISSING
        url = "https://www.jacques.de/weindepots/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "Results List"}).findAll("a")
        for loc in loclist:
            if "Großraum" in loc.text:
                continue
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = strip_accents(loc.text)
            street_address = strip_accents(
                soup.find("span", {"itemprop": "streetAddress"}).text
            )
            city = strip_accents(
                soup.find("span", {"itemprop": "addressLocality"}).text
            )
            if "-" in city:
                city = city.split("-")[0]
            zip_postal = soup.find("span", {"itemprop": "postalCode"}).text
            phone = soup.find("span", {"itemprop": "telephone"}).text
            hour_list = soup.findAll("span", {"itemprop": "openingHours"})
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = hours_of_operation + " " + hour["datetime"]
            latitude, longitude = (
                soup.select_one("img[src*=maps]")["src"]
                .split("center=", 1)[1]
                .split("&", 1)[0]
                .split(",")
            )
            country_code = "DE"
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
                latitude=latitude,
                longitude=longitude,
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
