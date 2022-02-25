from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "tph.ca"
API_URL = "https://www.tph.ca/wp-content/uploads/agile-store-locator/locator-data.json?v=1&action=asl_load_stores&load_all=1&layout=1"
SINGLE_STORE = "https://www.tph.ca/myaccount/API/Branch/BranchesByBranchNo?ID={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        store_number = row["website"].replace("https://www.tph.ca/", "").strip()
        page_url = row["website"]
        info = session.get(SINGLE_STORE.format(store_number), headers=HEADERS).json()
        location_name = info["Name"]
        if "CLOSED" in location_name.upper():
            continue
        street_address = row["street"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["postal_code"]
        phone = row["phone"]
        country_code = "CA"
        location_type = "The Printing House"
        latitude = row["lat"]
        longitude = row["lng"]
        if info["HoursFri"] == info["HoursMToT"]:
            hoo = "Mon - Fri: " + info["HoursFri"]
        else:
            hoo = hoo = "Mon: " + info["HoursMToT"] + ", Fri:" + info["HoursFri"]
        hours_of_operation = (
            hoo + ", Sat:" + info["HoursSat"] + ", Sun:" + info["HoursSun"]
        )
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
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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
