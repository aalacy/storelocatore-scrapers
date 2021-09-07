from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "firstonsite.com"
BASE_URL = "https://firstonsite.com"
LOCATION_URL = "https://firstonsite.com/locations/"
API_URL = "https://firstonsite.com/wp-json/inr/v1/locations"
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
    store_info = session.get(API_URL, headers=HEADERS).json()
    for country in store_info["locations"]:
        for row in store_info["locations"][country]:
            page_url = LOCATION_URL
            location_name = row["title"]
            store_number = row["id"]
            phone = row["localPhoneNumber"]["e164"]
            address = row["address"]
            if address["street2"]:
                street_address = f'{address["street1"]}, {address["street2"]}'
            else:
                street_address = address["street1"]
            city = address["city"]
            state = address["state"]
            zip_postal = address["zip"]
            country_code = row["localPhoneNumber"]["country"]
            hours_of_operation = MISSING
            location_type = "firstonsite"
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
                raw_address=f"{street_address}, {city}, {state} {zip_postal}",
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
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
