from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgSelenium
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "bunnings.com.au"
LOCATION_URL = "https://www.bunnings.com.au/shop/storelocator"
API_URL = "https://api.prod.bunnings.com.au/v1/stores/country/AU?fields=FULL"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def get_token():
    log.info("Geting token from selenium...")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    cookies = driver.get_cookies()
    for row in cookies:
        if "guest-token-storage" in row["name"]:
            return row["value"]
    return False


def fetch_data():
    log.info("Fetching store_locator data")
    token = json.loads(get_token())["token"]
    headers = {
        "Accept": "*/*",
        "Authorization": "Bearer " + token,
        "clientId": "mHPVWnzuBkrW7rmt56XGwKkb5Gp9BJMk",
        "country": "AU",
        "locale": "en_AU",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    }
    data = session.get(API_URL, headers=headers).json()
    for row in data["data"]["pointOfServices"]:
        location_name = row["displayName"]
        street_address = row["address"]["line1"]
        city = row["address"]["firstName"]
        state = row["address"]["region"]["name"]
        zip_postal = row["address"]["postalCode"]
        phone = row["address"]["phone"]
        country_code = row["address"]["country"]["isocode"]
        store_number = row["name"]
        hoo = ""
        for hday in row["openingHours"]["weekDayOpeningList"]:
            day = hday["weekDay"]
            if not hday["closed"]:
                hours = (
                    hday["openingTime"]["formattedHour"]
                    + " - "
                    + hday["closingTime"]["formattedHour"]
                )
            else:
                hours = "CLOSED"
            hoo += day + ": " + hours + ","
        hours_of_operation = hoo.rstrip(",")
        latitude = row["geoPoint"]["latitude"]
        longitude = row["geoPoint"]["longitude"]
        location_type = row["type"]
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
