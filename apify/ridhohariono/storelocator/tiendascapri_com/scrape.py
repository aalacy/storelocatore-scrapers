import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

DOMAIN = "tiendascapri.com"
BASE_URL = "https://www.tiendascapri.com/"
LOCATION_URL = "https://tiendascapri.com/tiendas/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    data = json.loads(
        re.search(
            r"=\s(.*);jQuery",
            soup.find("script", string=re.compile(r"mapsvg_options.*")).string,
        ).group(1)
    )
    for row in data["options"]["data_objects"]["objects"]:
        location_name = row["title"]
        addr = row["location"]["address"]
        raw_address = addr["formatted"]
        street_address = (
            MISSING if "route_short" not in addr else addr["route_short"].strip()
        )
        if "street_number" in addr:
            street_address = addr["street_number"] + " " + street_address
        if street_address == MISSING:
            street_address = addr["formatted"].split(",")[0].strip()
        city = addr["locality"]
        state = MISSING
        zip_postal = (
            MISSING if "postal_code" not in addr else addr["postal_code"].strip()
        )
        if "PR-693" in street_address:
            zip_postal = "00646"
        if "The Outlets at Montehiedra" in location_name:
            zip_postal = "00926"
        country_code = addr["country_short"]
        phone = row["telephone"]
        hours_of_operation = MISSING
        location_type = MISSING
        store_number = row["id"]
        latitude = row["location"]["geoPoint"]["lat"]
        longitude = row["location"]["geoPoint"]["lng"]
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
            raw_address=raw_address,
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
