from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "interbank.pe"
BASE_URL = "https://interbank.pe"
LOCATION_URL = "https://interbank.pe/puntos-de-atencion"
API_URL = "https://interbank.pe/puntos-de-atencion?p_p_id=pe_com_ibk_halcon_attentionpoints_internal_portlet_AttentionPointsWebPortlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=%2FattentionpointsFilterMVCResourceCommand&p_p_cacheability=cacheLevelPage&_pe_com_ibk_halcon_attentionpoints_internal_portlet_AttentionPointsWebPortlet_cmd=filter&lat={}&lng={}"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
    "Referer": LOCATION_URL,
    "sec-fetch-mode": "cors",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"

session = SgRequests(verify_ssl=False)


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
        country_codes=[SearchableCountries.PERU],
        expected_search_radius_miles=5,
        max_search_results=2,
    )
    for lat, long in search:
        url = API_URL.format(lat, long)
        log.info(f"Searching locations for => {lat}, {long}")
        stores = session.get(url, headers=HEADERS).json()
        for row in stores["results"]:
            search.found_location_at(lat, long)
            location_name = row["titulo"]
            raw_address = row["direccion"].strip()
            street_address, city, state, zip_postal = getAddress(raw_address)
            if street_address == "S /N":
                street_address = raw_address
            country_code = "PE"
            phone = row["telefono"] or MISSING
            hours_of_operation = row["horario"]
            if hours_of_operation in "En función del local":
                hours_of_operation = MISSING
            location_type = row["tipo"]
            store_number = row["id"]
            latitude = row["latitud"]
            longitude = row["longitud"]
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
