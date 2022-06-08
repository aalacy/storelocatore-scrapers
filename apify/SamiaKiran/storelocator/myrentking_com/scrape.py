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
website = "myrentking_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.myrentking.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://www.myrentking.com/store_finder.html"
    r = session.get(url, headers=headers)
    loclist = r.text.split("var locations = [")[1].split(
        "// Render the locations using the array", 1
    )[0]
    loclist = loclist.replace("];", "")
    pattern = re.compile(r"\s\s+")
    loclist = re.sub(pattern, "\n", loclist)
    loclist = "[" + loclist.rsplit("},", 1)[0] + "}]"
    loclist = json.loads(loclist)
    for loc in loclist:
        location_name = loc["store_name"]
        latitude = loc["latitude"]
        longitude = loc["longitude"]
        page_url = DOMAIN + loc["url"]
        street_address = loc["address"]
        city = loc["city"]
        state = loc["state"]
        zip_postal = loc["zip"]
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        phone = (
            soup.select("a[href*=tel]")[1]
            .get_text(separator="|", strip=True)
            .replace("|", "")
        )
        hours_of_operation = (
            soup.find("div", {"id": "location-hours-section"})
            .find("table")
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        if "Coming Soon" in hours_of_operation:
            continue
        country_code = "US"
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
