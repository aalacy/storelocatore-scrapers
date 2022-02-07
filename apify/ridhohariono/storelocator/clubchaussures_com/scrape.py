from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgSelenium
import json
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "clubchaussures.com"
BASE_URL = "https://clubchaussures.com/boutique"
LOCATION_URL = "https://clubchaussures.com/trouver-boutique/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "origin": BASE_URL,
    "referer": BASE_URL,
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
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    soup = bs(driver.page_source, "lxml")
    contents = soup.find(
        "script",
        string=re.compile(r"AmLocation\.Amastyload.*"),
    )
    data = json.loads(
        re.search(
            r'AmLocation\.Amastyload\(\{"totalRecords":31,"items":(.*)\}\);',
            contents.string,
        ).group(1)
    )
    for row in data:
        location_name = row["name"]
        street_address = row["address"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["zip"]
        country_code = row["country"]
        phone = row["phone"]
        hours_of_operation = (
            re.sub(
                r"\* L'horaire.*|L'horaire.*",
                "",
                bs(row["description"], "lxml").get_text(strip=True, separator=","),
            )
            .rstrip(",")
            .strip()
        )
        store_number = row["position"]
        location_type = MISSING
        latitude = row["lat"]
        longitude = row["lng"]
        page_url = BASE_URL + "?store=" + store_number
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
    driver.quit()


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
