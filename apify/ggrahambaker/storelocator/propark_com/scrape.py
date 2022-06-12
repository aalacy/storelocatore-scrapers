from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import re
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "propark.com"
BASE_URL = "https://stores.propark.com/"
LOCATION_URL = "https://www.propark.com/search/"
LOCATION_FORMAT = "https://www.propark.com/search/?lat={}&lng={}"
API_URL = "https://www.propark.com/wp-admin/admin-ajax.php"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def get_latlong(url):
    latlong = re.search(r"center=(-?[\d]*\.[\d]*),(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def get_all_stores_ids(latitude, longitude):
    payloads = {
        "action": "hourly_parking_query",
        "showAllFacilities": "true",
        "lat": latitude,
        "lng": longitude,
        "radius": "100",
    }
    ids = []
    req = session.post(API_URL, headers=HEADERS, data=payloads).json()
    if req["status"] == "success":
        ids = req["facilityIds"]
    log.info(f"Found ({len(ids)}) stores id {latitude, longitude}")
    return ids


def get_store_by_id(store_id):
    log.info(f"Get contents with store id: {store_id}")
    payloads = {
        "action": "facility_modal",
        "facilityId": store_id,
        "parkingType": "hourly",
    }
    req = session.post(API_URL, headers=HEADERS, data=payloads)
    try:
        check = req.json()
        if "have_posts" in check:
            return False
    except:
        pass
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=20,
    )
    for lat, lng in search:
        store_ids = get_all_stores_ids(lat, lng)
        if len(store_ids) > 0:
            search.found_location_at(lat, lng)
        for row in store_ids:
            soup = get_store_by_id(row)
            if not soup:
                continue
            location_name = soup.find("h1", {"class": "card-header-title"}).text
            raw_address = (
                soup.find("section", {"id": "directions"}).find("p").text.strip()
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = soup.find("a", {"href": re.compile(r"tel:.*")})
            if not phone:
                phone = MISSING
            else:
                phone = phone.text.strip()
            hours_of_operation = (
                soup.find("section", {"id": "hours"})
                .find("ul")
                .get_text(strip=True, separator=",")
            )
            store_number = row
            country_code = "US"
            location_type = "propark"
            latlong = soup.find("article", {"class": "card"})
            latitude = latlong["data-latitude"]
            longitude = latlong["data-longitude"]
            page_url = LOCATION_FORMAT.format(latitude, longitude)
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
                    SgRecord.Headers.STORE_NUMBER,
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
