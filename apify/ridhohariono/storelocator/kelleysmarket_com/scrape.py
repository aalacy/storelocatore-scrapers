from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "kelleysmarket.com"
LOCATION_URL = "https://kelleysmarket.com/find-a-market/"
API_URL = "https://kelleysmarket.com/wp-json/wp/v2/locations?per_page=100"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        page_url = row["link"]
        info = row["meta"]
        location_name = row["title"]["rendered"]
        street_address = info["_wse_wp_text_field_address"][0].strip()
        city = info["_wse_wp_text_field_city"][0].strip()
        state = info["_wse_wp_text_field_state"][0].strip()
        zip_postal = info["_wse_wp_text_field_zip"][0].strip()
        country_code = "US"
        phone = info["_wse_wp_text_field_phone_number"][0].strip()
        hours_of_operation = (
            bs(info["_wse_wp_text_field_alcohol_hours"][0], "lxml").get_text(
                strip=True, separator=","
            )
            or "Open 24 hours"
        )
        store_number = row["id"]
        location_type = MISSING
        latitude = info["_wse_wp_text_field_latitude"][0]
        longitude = info["_wse_wp_text_field_longitude"][0]
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
