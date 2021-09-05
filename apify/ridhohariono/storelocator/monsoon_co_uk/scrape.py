import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import (
    DynamicZipSearch,
    SearchableCountries,
)
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "monsoon.co.uk"
BASE_URL = "https://www.monsoon.co.uk"
LOCATION_URL = "https://stores.monsoon.co.uk/"
API_URL = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location={}&limit=50&api_key={}&v=20181201&resolvePlaceholders=true&languages=en_GB&entityTypes=location&savedFilterIds=545514960"
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(hour_content):
    hoo = []
    for day in hour_content:
        if "isClosed" in hour_content[day]:
            hoo.append(day + ": CLOSED")
        else:
            start = str(hour_content[day]["openIntervals"][0]["start"])
            end = str(hour_content[day]["openIntervals"][0]["end"])
            hours = "{}:{} - {}:{}".format(start[:2], start[-2:], end[:2], end[-2:])
            hoo.append(day + ": " + hours)
    return ", ".join(hoo)


def get_api_key():
    log.info("Get Api Key...")
    r = session.get(LOCATION_URL, headers=HEADERS)
    api_key = re.search(r'var liveAPIKey = "(.*)"\.trim\(\)\;', r.text)
    return api_key.group(1)


def fetch_store_data(zip_search, api_key):
    log.info("Fetching store Locatior by ZIP: " + zip_search)
    info = session.get(API_URL.format(zip_search, api_key), headers=HEADERS).json()
    return info


def fetch_data():
    log.info("Fetching store_locator data")
    api_key = get_api_key()
    search = DynamicZipSearch(
        country_codes=SearchableCountries.SovereigntyGroups["UK"],
        max_search_distance_miles=100,
        expected_search_radius_miles=10,
    )
    zip_codes = []
    for zip in search:
        zip_codes.append(zip)
    log.info(f"Searching for ({len(zip_codes)})...")
    for zip_search in zip_codes:
        store_list = fetch_store_data(zip_search, api_key)["response"]["entities"]
        log.info(f"Append ({len(store_list)}) locations with zip code: {zip_search}")
        for row in store_list:
            page_url = row["landingPageUrl"]
            location_name = handle_missing(row["c_aboutSectionHeading"])
            if "line2" in row["address"] and len(row["address"]["line2"]) > 0:
                street_address = "{}, {}".format(
                    row["address"]["line1"], row["address"]["line2"]
                )
            else:
                street_address = handle_missing(row["address"]["line1"])
            city = handle_missing(row["address"]["city"])
            state = MISSING
            zip_postal = handle_missing(row["address"]["postalCode"])
            country_code = handle_missing(row["address"]["countryCode"])
            phone = handle_missing(row["mainPhone"])
            hours_of_operation = parse_hours(row["hours"])
            store_number = row["meta"]["id"]
            sub_hoo = re.sub(r"[a-z]*:\s+", "", hours_of_operation, flags=re.IGNORECASE)
            if all(value == "CLOSED" for value in sub_hoo.split(",")):
                location_type = "TEMP_CLOSED"
            else:
                location_type = "OPEN"
            latitude = handle_missing(row["yextDisplayCoordinate"]["latitude"])
            longitude = handle_missing(row["yextDisplayCoordinate"]["longitude"])
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
                raw_address=f"{street_address}, {city}, {zip_postal}",
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
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
