from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import json

DOMAIN = "storagecourt.com"
BASE_URL = "https://www.storagecourt.com"
LOCATION_URL = "https://www.storagecourt.com/self-storage"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("a.ogep3VRb_llXipWczX6wu")
    for row in contents:
        page_url = BASE_URL + row["href"]
        store = pull_content(page_url)
        info = json.loads(
            store.find(
                "script", type="application/ld+json", string=re.compile(r'"latitude.*')
            ).string
        )
        location_name = info["name"].strip()
        street_address = info["address"]["streetAddress"]
        city = info["address"]["addressLocality"]
        state = info["address"]["addressRegion"]
        zip_postal = info["address"]["postalCode"]
        country_code = "US"
        phone = info["telephone"]
        store_number = MISSING
        hours = (
            store.find("span", text=re.compile(r"HOURS|WINTER HOURS"))
            .parent.parent.text.split("OFFICE HOURS", 1)[1]
            .split("ACCESS HOURS", 1)[0]
            .replace("CLOSED", "CLOSED ")
            .replace("pm", "pm ")
            .replace("PM", "PM ")
        )
        hours_of_operation = re.sub(
            r"\s\s+|\(.*\)|The office is operated remotely during these hours:",
            " ",
            hours,
        ).strip()
        location_type = info["@type"]
        latitude = info["geo"]["latitude"]
        longitude = info["geo"]["longitude"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
