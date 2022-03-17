from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "sonesta.com"
BASE_URL = "https://www.sonesta.com"
LOCATION_URL = "https://www.sonesta.com/sonesta-hotels-resorts/"
API_URL = "https://core.rlhco.com/api/hotel-proximity?_format=json&site_id=31&coordinates[value]=50000&coordinates[source_configuration][origin][lat]={}&coordinates[source_configuration][origin][lon]={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "api-key": "3bbd8f466bac4cfeab1d966865b5efac",
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


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.CHILE,
            SearchableCountries.COLOMBIA,
            SearchableCountries.ECUADOR,
            SearchableCountries.EGYPT,
            SearchableCountries.PERU,
        ],
        expected_search_radius_miles=1000,
        max_search_results=100,
    )
    coords = []
    for lat, long in search:
        coords.append([lat, long])
    coords.append([18.0404, -63.1209])
    for lat, long in coords:
        url = API_URL.format(lat, long)
        data = session.get(url, headers=HEADERS).json()
        for row in data:
            if row["brand_code"] != "SHR":
                continue
            page_url = BASE_URL + row["path"]
            location_name = row["name"].replace("&amp;", "&").strip()
            raw_address = bs(row["address"], "lxml").get_text(strip=True).strip()
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = row["phone"].strip()
            hours_of_operation = MISSING
            location_type = row["brand"].replace("&amp;", "&").strip()
            store_number = row["id"]
            country_code = MISSING
            coord = row["coordinates"].split(" ")
            latitude, longitude = coord
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
