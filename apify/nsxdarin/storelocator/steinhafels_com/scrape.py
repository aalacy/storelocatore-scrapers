from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "steinhafels.com"
BASE_URL = "https://www.steinhafels.com/store/"
LOCATION_URL = "https://www.steinhafels.com/store/directory"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_token():
    soup = pull_content(LOCATION_URL)
    content = soup.find("script", id="app-state")
    token = re.search(
        r'api\.blueport\.com\/v1\/store\?key=(.*)&a;storeKey=\d+":',
        content.string.replace("&q;", '"'),
    )
    return token.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    token = get_token()
    data = session.get(
        f"https://api.blueport.com/v1/store?key={token}", headers=HEADERS
    ).json()
    for row in data["stores"]:
        if "storeUrl" in row:
            page_url = BASE_URL + row["storeUrl"]
        else:
            page_url = LOCATION_URL
        if "thoroughfare" not in row["storeAddress"]:
            continue
        location_name = row["storeName"]
        if "CORP/WHSE" in location_name:
            continue
        street_address = row["storeAddress"]["thoroughfare"]
        city = row["storeAddress"]["locality"]
        state = row["storeAddress"]["administrativeArea"]
        zip_postal = row["storeAddress"]["postalCode"]
        country_code = row["storeAddress"]["country"]
        phone = (
            row["storeAddress"]["telephone"]
            if "telephone" in row["storeAddress"]
            else MISSING
        )
        hoo = ""
        for hday in row["storeHours"]:
            hoo += hday["day"] + ": " + hday["storeHours"] + ","
        hours_of_operation = hoo.rstrip(",")
        store_number = row["storeKey"]
        if "metaContexts" in row:
            location_type = row["metaContexts"][0]["metaValue"]
        else:
            location_type = MISSING
        if "Coming Soon" in location_name:
            location_type = "COMING_SOON"
        latitude = row["latitude"] if "latitude" in row else MISSING
        longitude = row["longitude"] if "longitude" in row else MISSING
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
