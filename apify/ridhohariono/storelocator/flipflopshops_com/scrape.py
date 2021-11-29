from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import (
    DynamicGeoSearch,
    SearchableCountries,
)

DOMAIN = "flipflopshops.com"
LOCATION_URL = "https://flipflopshops.com/stores/"
API_URL = "https://flipflopshops.locally.com/geo/point/{}/{}?switch_user_location=1"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


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


def getTime(start, end):
    if start == 0 and end == 0:
        return "Closed"
    start = str(start)
    end = str(end)
    if len(start) == 3:
        start = "0" + str(start)
    if len(end) == 3:
        end = "0" + str(end)
    start = start[:2] + ":" + start[2:]
    end = end[:2] + ":" + end[2:]
    return start + "-" + end


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
    )
    for lat, long in search:
        url = API_URL.format(lat, long)
        log.info("Fetch data from => " + url)
        data = session.get(url, headers=HEADERS).json()
        for key, val in data["nearest_stores"]["data"].items():
            store_number = val["id"]
            search.found_location_at(lat, long)
            page_url = f"https://flipflopshops.locally.com/hosted/redirect/14484/{store_number}"
            location_name = val["name"].strip()
            street_address = val["address"].strip()
            city = val["city"]
            state = val["state"]
            zip_postal = val["zip"]
            phone = val["phone"]
            country_code = val["country"]
            hours_of_operation = (
                "Monday: "
                + getTime(val["mon_time_open"], val["mon_time_close"])
                + ","
                + "Tuesday: "
                + getTime(val["tue_time_open"], val["tue_time_close"])
                + ","
                + "Wednesday: "
                + getTime(val["wed_time_open"], val["wed_time_close"])
                + ","
                + "Thursday: "
                + getTime(val["thu_time_open"], val["thu_time_close"])
                + ","
                + "Friday: "
                + getTime(val["fri_time_open"], val["fri_time_close"])
                + ","
                + "Saturday: "
                + getTime(val["sat_time_open"], val["sat_time_close"])
                + ","
                + "Sunday: "
                + getTime(val["sun_time_open"], val["sun_time_close"])
            ).strip()
            location_type = MISSING
            latitude = val["lat"]
            longitude = val["lng"]
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
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
