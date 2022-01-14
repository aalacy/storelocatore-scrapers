from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "bancofcal.com"
API_URL = "https://bancofcal.com/wp-admin/admin-ajax.php?action=search_ajax_locations&dataType=xml&_=1638357298779"
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
    soup = bs(session.get(API_URL, headers=HEADERS).json()["data"], "lxml")
    contents = soup.find("markers").find_all("marker")
    for row in contents:
        page_url = row["permalink"]
        location_name = row["name"].replace("&#8211;", "-")
        street_address = row["address"].strip()
        city_state_zip = row["city_state_zip"].split(",")
        city = city_state_zip[0]
        state = re.sub(r"\d+", "", city_state_zip[1]).strip()
        zip_postal = re.sub(r"\D+", "", city_state_zip[1]).strip()
        phone = row["phone"]
        country_code = "US"
        store_number = row["id"]
        hours_of_operation = row["times"]
        if "Temporarily Closed" in row["branch_status"]:
            location_type = "TEMP_CLOSED"
        else:
            location_type = row["features"].strip()
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
