from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "greenhalghs.com"
BASE_URL = "https://www.greenhalghs.com"
LOCATION_URL = "https://www.greenhalghs.com/stores/"
API_URL = "https://www.greenhalghs.com/wp-admin/admin-ajax.php?action=store_search&lat=53.58154&lng=-2.52123&max_results=1000&search_radius=50&autoload=1"
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
    store_info = session.get(API_URL).json()
    for row in store_info:
        page_url = row["url"] if BASE_URL in row["url"] else BASE_URL + row["url"]
        location_name = row["address"]
        store_number = MISSING
        phone = row["phone"]
        street_address = row["address2"]
        city = row["city"]
        state = MISSING
        zip_postal = row["zip"]
        country_code = "UK" if row["country"] == "United Kingdom" else row["country"]
        try:
            hoo_content = bs(row["hours"], "lxml")
            hours_of_operation = (
                hoo_content.find("table")
                .get_text(strip=True, separator=",")
                .replace("day,", "day:")
            )
        except:
            hours_of_operation = MISSING
        location_type = "greenhalghs"
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
