from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "countdown.co.nz"
LOCATION_URL = "https://shop.countdown.co.nz/store-finder/"
API_URL = "https://api.cdx.nz/site-location/api/v1/sites?latitude=-39.6383285&longitude=176.8387971&maxResults=10000"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data["siteDetail"]:
        info = row["site"]
        location_name = info["name"].strip()
        if info["addressLine2"]:
            street_address = info["addressLine1"] + " " + info["addressLine2"].strip()
        else:
            street_address = info["addressLine1"].strip()
        city = info["suburb"].strip()
        state = info["state"]
        zip_postal = info["postcode"]
        phone = info["phone"]
        country_code = "NZ"
        store_number = info["id"]
        location_type = info["division"]
        hoo = ""
        for day, hour in row["tradingHours"][0].items():
            if day == "date":
                continue
            hoo += (
                day.title()
                + ": "
                + re.sub(r":00$", "", hour["startTime"])
                + "-"
                + re.sub(r":00$", "", hour["endTime"])
                + ","
            )
        hours_of_operation = hoo.rstrip(",")
        latitude = info["latitude"]
        longitude = info["longitude"]
        page_url = (
            LOCATION_URL
            + str(store_number)
            + "/"
            + city.lower().replace(",", "").replace(" ", "-")
            + "/"
            + location_name.lower().replace(",", "").replace(" ", "-")
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
