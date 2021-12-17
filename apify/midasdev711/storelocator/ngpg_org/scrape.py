from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "ngpg_org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.ngpg.org/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.ngpg.org/fm/index/practice-map-data"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("marker")
        for loc in loclist:
            location_type = loc["category"]
            street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["postal"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            phone = loc["phone"]
            location_name = loc["name"]
            page_url = "https://www.ngpg.org" + loc["web"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                hours_of_operation = (
                    soup.find("table", {"class": "hours-table"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Open Close", "")
                )
            except:
                try:
                    hours_of_operation = (
                        soup.find("div", {"class": "location-hours"})
                        .findAll("p")[1]
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                except:
                    try:
                        hours_of_operation = (
                            soup.find("div", {"class": "location-hours"})
                            .find("p")
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                        )
                    except:
                        hours_of_operation = MISSING
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
                location_type=location_type,
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
