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
website = "globus_ch"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}


DOMAIN = "https://globus.ch"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.globus.ch/filialsuche"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div", {"data-testid": "storefinder-index-store-container"}
        )
        for loc in loclist:
            page_url = DOMAIN + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            loc = r.text.split('"address":')[1].split(',"distance":')[0]
            location_name = strip_accents(
                r.text.split('"item":{"@id":"#","name":"')[2].split('"')[0]
            )
            street_address = loc.split('"street":"')[1].split('"')[0]
            city = strip_accents(loc.split('"city":"')[1].split('"')[0])
            zip_postal = loc.split('"zip":"')[1].split('"')[0]
            state = loc.split('"country":"')[1].split('"')[0]
            country_code = loc.split('"countryCode":"')[1].split('"')[0]
            latitude, longitude = (
                loc.split('"coordinates":[')[1].split("]")[0].split(",")
            )
            phone = r.text.split('"phone":"')[1].split('"')[0]
            store_number = r.text.split('"storeID":"')[1].split('"')[0]
            hour_list = json.loads(
                r.text.split('"openingTimes":')[1].split("}}]")[0] + "}}]"
            )
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["day"]
                time = hour["timePeriod"]["from"] + "-" + hour["timePeriod"]["to"]
                final = day + " " + time
                hours_of_operation = hours_of_operation + " " + final
            hours_of_operation = hours_of_operation.replace("Sunday -", "Sunday Closed")
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
