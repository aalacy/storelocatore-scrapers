import json
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
website = "ellis_be"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://ellis.be/en-be/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://ellis.be/en-be/restaurants/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("let restaurants = ")[1].split("}];")[0]
        loclist = json.loads(loclist + "}]")
        for loc in loclist:
            location_name = html.unescape(strip_accents(loc["name"]))
            log.info(location_name)
            store_number = loc["id"]
            page_url = loc["url"]
            phone = loc["phone"]
            street_address = strip_accents(loc["address"])
            city = strip_accents(loc["city"])
            state = MISSING
            zip_postal = loc["zip"]
            latitude = loc["location"]["lat"]
            longitude = loc["location"]["lng"]
            hours_of_operation = (
                BeautifulSoup(loc["hours"], "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if hours_of_operation == "Closed":
                hours_of_operation = MISSING
            if (
                city == "Amsterdam"
                or city == "Breda"
                or city == "Rotterdam"
                or city == "Utrecht"
            ):
                country_code = "Netherlands"
            else:
                country_code = "Belgium"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
