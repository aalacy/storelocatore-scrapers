import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "myburgerusa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://www.myburgerusa.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.myburgerusa.com/find-us/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("locations: [")[1].split("[]}}]")[0].split("[]}}, ")
        for loc in loclist:
            loc = loc.split(', "google_place_id"')[0]
            loc = json.loads(loc + "}")
            page_url = DOMAIN + loc["url"]
            log.info(page_url)
            location_name = loc["name"]
            store_number = loc["id"]
            phone = loc["phone_number"]
            street_address = loc["street"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal_code"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            hours_of_operation = loc["hours"]
            hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
            hours_of_operation = (
                hours_of_operation.get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("NORMAL HOURS Open", "")
            )
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
