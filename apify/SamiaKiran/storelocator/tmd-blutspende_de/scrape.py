import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "blutspende_de"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://tmd-blutspende.de/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.tmd-blutspende.de/standorte/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "location"})
        for loc in loclist:
            page_url = loc["href"]
            if "www.tmd-blutspende.de" not in page_url:
                continue
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.find("script", {"type": "application/ld+json"}).text
            temp = json.loads(temp)
            location_name = temp["name"]
            phone = temp["telephone"]
            address = temp["address"]
            street_address = strip_accents(address["streetAddress"])
            city = strip_accents(address["addressLocality"])
            state = MISSING
            zip_postal = address["postalCode"]
            country_code = address["addressCountry"]
            latitude = temp["geo"]["latitude"]
            longitude = temp["geo"]["longitude"]
            hour_list = temp["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                day = (
                    str(hour["dayOfWeek"])
                    .replace("', '", ",")
                    .replace("['", "")
                    .replace("']", "")
                )
                time = hour["opens"] + "-" + hour["closes"]
                hours_of_operation = hours_of_operation + " " + day + " " + time
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
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
