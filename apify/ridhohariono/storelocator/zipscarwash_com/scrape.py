import time
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import SearchableCountries, DynamicZipAndGeoSearch
import re

DOMAIN = "zipscarwash.com"
BASE_URL = "https://www.zipscarwash.com/"
LOCATION_URL = "https://www.zipscarwash.com/drive-through-car-wash-locations?code={code}&latitude={latitude}&longitude={longitude}&distance=500"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    max_results = 10
    max_distance = 500
    search = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )
    for zipcode, coord in search:
        lat, long = coord
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, long, search.items_remaining())
        )
        page_url = LOCATION_URL.format(code=zipcode, latitude=lat, longitude=long)
        try:
            soup = pull_content(page_url)
        except:
            time.sleep(2)
            soup = pull_content(page_url)
        store_content = soup.find_all(
            "div",
            {
                "class": "locations__results-unit flex align-items-center justify-between"
            },
        )
        for row in store_content:
            location_name = row.find(
                "div", {"class": "locations__results-name"}
            ).text.strip()
            search.found_location_at(lat, long)
            raw_address = row.find(
                "div", {"class": "locations__results-address"}
            ).get_text(strip=True, separator=",")
            street_address, city, state, zip_postal = getAddress(raw_address)
            country_code = "US"
            phone = MISSING
            store_number = MISSING
            location_type = MISSING
            latlong = (
                row.find("a", {"href": re.compile(r"\/maps\/place.*")})["href"]
                .replace("https://www.google.com/maps/place/", "")
                .split(",")
            )
            latitude = latlong[0]
            longitude = latlong[1]
            hours_of_operation = row.find(
                "div", {"class": "locations__results-hours"}
            ).get_text(strip=True, separator=",")
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
                raw_address=raw_address,
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
            ),
            duplicate_streak_failure_factor=250000,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
