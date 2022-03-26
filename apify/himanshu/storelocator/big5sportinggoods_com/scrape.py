import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipAndGeoSearch, SearchableCountries


DOMAIN = "big5sportinggoods.com"
LOCATION_URL = "http://big5sportinggoods.com/store/integration/find_a_store.jsp?storeLocatorAddressField={}&miles=100&lat={}&lng={}&showmap=yes"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 200:
        soup = bs(req.content, "lxml")
        return soup
    return False


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=100,
        max_search_results=500,
    )
    for zipcode, coord in search:
        page_url = LOCATION_URL.format(zipcode, coord[0], coord[1])
        soup = pull_content(page_url)
        if not soup:
            continue
        stores = soup.select("div.store-address")
        log.info(f"Found ({len(stores)}) locations with coord => {coord[0]},{coord[1]}")
        for row in stores:
            info = row.find("div", {"class": "map-directions-link"})
            location_name = info.find("input", {"name": "name"})["value"]
            street_address = re.sub(
                r".$|,$|.\s$|,\s$|\(.*\)",
                "",
                info.find("input", {"name": "address"})["value"].strip(),
            ).strip()
            city = re.sub(
                r"\(.*\)", "", info.find("input", {"name": "city"})["value"]
            ).strip()
            state = info.find("input", {"name": "state"})["value"]
            zip_postal = info.find("input", {"name": "postalCode"})["value"]
            country_code = "US"
            phone = info.find("input", {"name": "phonenumber"})["value"]
            try:
                hours_of_operation = row.find("ul").get_text(strip=True, separator=",")
            except:
                hours_of_operation = MISSING
            location_type = MISSING
            store_number = location_name.split("#")[1].split(" - ")[0].strip()
            latitude = info.find("input", {"name": "lat"})["value"]
            longitude = info.find("input", {"name": "lng"})["value"]
            search.found_location_at(latitude, longitude)
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
            RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
