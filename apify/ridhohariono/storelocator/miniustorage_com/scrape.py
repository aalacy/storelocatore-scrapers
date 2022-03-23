import json
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


DOMAIN = "miniustorage.com"
BASE_URL = "https://www.miniustorage.com"
LOCATION_URL = "https://www.miniustorage.com/locations/"
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
    soup = pull_content(BASE_URL)
    contents = soup.find("script", string=re.compile(r"var candee_js_variables.*"))
    data = json.loads(
        re.search(r"candee_js_variables\s+= ({.*});", contents.string).group(1)
    )
    for row in data["facilities"]:
        page_url = row["permalink"]
        location_name = row["facility_name"].strip()
        street_address = row["facility_address"].strip()
        city = row["facility_city"]
        state = row["facility_region"]
        zip_postal = row["facility_zipcode"]
        country_code = (
            "US" if row["facility_country"] == "USA" else row["facility_country"]
        )
        phone = row["facility_phone"]
        hours_of_operation = MISSING
        location_type = MISSING
        store_number = row["prop_id"]
        latitude = row["lat"]
        longitude = row["lng"]
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
