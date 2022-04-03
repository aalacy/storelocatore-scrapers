import re
import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "honeygrow_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.honeygrow.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    r = session.get(DOMAIN)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("script", {"type": "application/ld+json"}).text
    loclist = json.loads(data)
    loclist = loclist["subOrganization"]
    for loc in loclist:
        phone = loc["telephone"]
        street_address = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        zip_postal = loc["address"]["postalCode"]
        location_name = loc["address"]["name"]
        page_url = loc["url"]
        if "coming-soon" in page_url:
            continue
        log.info(page_url)
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        longitude = soup1.find("div", {"class": "gmaps"})["data-gmaps-lng"]
        latitude = soup1.find("div", {"class": "gmaps"})["data-gmaps-lat"]
        hours_of_operation = (
            soup1.find_all("div", {"class": "col-md-6"})[0]
            .text.replace("NOW OPEN!", "")
            .replace("day", "day ")
            .replace("Located in Ellisburg Shopping Center", "")
            .split("\n")[-2]
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        if "CLOSED until further notice" in hours_of_operation:
            hours_of_operation = "Temporarily CLOSED"
        country_code = "US"
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
