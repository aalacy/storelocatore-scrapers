from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import re


DOMAIN = "peteralexander.com.au"
STORE_URL = (
    "https://www.peteralexander.com.au/shop/en/peteralexander/stores/au/act/woden"
)
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
    soup = pull_content(STORE_URL)
    data = json.loads(soup.find("div", id="storeSelection").string)["storeLocator"]
    for row in data:
        page_url = row["storeURL"]
        location_name = row["storeName"]
        street_address = re.sub(
            r"^.,|,.$|, .$|,$",
            "",
            (row["shopAddress"] + ", " + row["streetAddress"]).strip().rstrip(","),
        ).strip()
        city = row["city"]
        state = row["state"]
        zip_postal = row["zipcode"].replace(".", "").strip()
        country_code = row["country"]
        phone = row["phone"]
        hours_of_operation = (
            bs(row["storehours"], "lxml")
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .strip()
        ) or MISSING
        location_type = MISSING
        store_number = row["locId"]
        latitude = row["latitude"]
        longitude = row["longitude"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
