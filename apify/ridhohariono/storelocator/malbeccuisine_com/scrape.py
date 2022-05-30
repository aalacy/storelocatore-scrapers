from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import json

DOMAIN = "malbeccuisine.com"
LOCATION_URL = "https://www.malbeccuisine.com/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Referer": LOCATION_URL,
    "content-type": "text/plain",
    "origin": LOCATION_URL,
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def get_coord(data, phone):
    for key, value in data.items():
        if key.startswith("RestaurantLocation:"):
            if phone == value["phone"]:
                return value["lat"], value["lng"]
    return MISSING, MISSING


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find_all("script", {"type": "application/ld+json"})
    more_info = json.loads(
        soup.find("script", id="popmenu-apollo-state")
        .string.replace("window.POPMENU_APOLLO_STATE = ", "")
        .replace("};", "}")
        .replace('" + "', "")
        .strip()
    )
    for row in contents:
        info = json.loads(row.string)
        location_name = info["name"]
        street_address = info["address"]["streetAddress"]
        city = info["address"]["addressLocality"]
        state = info["address"]["addressRegion"]
        zip_postal = info["address"]["postalCode"]
        country_code = "US"
        phone = info["address"]["telephone"]
        store_number = MISSING
        location_type = info["@type"]
        latitude, longitude = get_coord(more_info, phone)
        hours_of_operation = (
            ",".join(info["openingHours"])
            .replace("Su", "Sunday:")
            .replace("Mo", "Monday:")
            .replace("Tu", "Tuesday:")
            .replace("We", "Wednesday:")
            .replace("Th", "Thursday:")
            .replace("Fr", "Friday:")
            .replace("Sa", "Saturday:")
        )
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
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
