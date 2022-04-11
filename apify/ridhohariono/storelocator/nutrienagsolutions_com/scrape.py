from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "nutrienagsolutions.com"
LOCATION_URL = "https://nutrienagsolutions.com/find-location"
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
    contents = soup.select("ul.locations li")
    for row in contents:
        location_name = row["data-title"].replace('"', "").strip()
        street_address = row["data-address"].replace("\n", ",").replace('"', "").strip()
        city = row["data-city"]
        state = row["data-state"]
        try:
            zip_postal = row["data-zipcode"]
        except:
            zip_postal = MISSING
        try:
            phone = row["data-phone"].replace('"', "").strip()
        except:
            phone = MISSING
        location_type = row["data-type"]
        country_code = "US"
        if len(zip_postal.split(" ")) > 1 or "Humboldt" in city:
            country_code = "CA"

        # Fix Broken HTML Structure
        if "RetailBranch" in city and len(zip_postal) == 2:
            city = state
            state = zip_postal
            zip_postal = MISSING
            location_type = "RetailBranch"
            street_address = row["data-type"]
            if phone == state:
                phone = MISSING
            if row["data-latitude"] == "CAN":
                country_code = "CA"
            else:
                country_code = "US"

        hours_of_operation = MISSING
        store_number = MISSING
        try:
            latitude = row["data-latitude"]
            longitude = row["data-longitude"]
            if "USA" in latitude or "CAN" in latitude:
                latitude = MISSING
                longitude = MISSING
        except:
            latitude = MISSING
            longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
            raw_address=f"{street_address}, {city}, {state}, {zip_postal}",
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
