from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "shopaplusrentals.com"
BASE_URL = "https://shopaplusrentals.com"
LOCATION_URL = "https://shopaplusrentals.com/api/v1/locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = SgRecord.MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hours(link_url):
    soup = pull_content(link_url)
    content = soup.find("h3", {"class": "business-hours-title"}).find_next(
        "div", {"class": "col-12 pl-0 pr-lg-2 pr-0"}
    )
    hoo = content.get_text(strip=True, separator=",")
    return hoo.replace("day,", "day: ").replace("Online Only", MISSING)


def fetch_data():
    store_info = session.post(LOCATION_URL, headers=HEADERS).json()
    for row in store_info["locations"]:
        page_url = BASE_URL + row["store_page"]
        location_name = row["name"]
        street_address = row["address"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["zipcode"]
        store_number = row["store_number"]
        phone = row["phone_number"]
        country_code = "US"
        latitude = row["latitude"]
        longitude = row["longitude"]
        location_type = MISSING
        if "ONLINE ONLY" in location_name or "Online Only" in street_address:
            location_type = "ONLINE ONLY"
            street_address = MISSING
            hours_of_operation = MISSING
        else:
            hours_of_operation = get_hours(page_url)
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
