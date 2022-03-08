from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "flipflopshops.com"
LOCATION_URL = "https://www.flipflopshops.com/pages/shop-locator"
API_URL = "https://flipflopshops.locally.com/stores/conversion_data?has_data=true&company_id=14484&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat={}&map_center_lng={}&map_distance_diag=3000.000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=8"
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


def fetch_data():
    log.info("Fetching store_locator data")
    fix_coord = [
        {"lat": -24.721393388152748, "lng": 134.48956260698222},
        {"lat": 21.300970635530234, "lng": -157.8556999999998},
        {"lat": 40.725444204821486, "lng": -73.98660000000041},
    ]
    for val in fix_coord:
        url = API_URL.format(val["lat"], val["lng"])
        data = session.get(url, headers=HEADERS).json()
        for row in data["markers"]:
            store_number = row["id"]
            page_url = f"https://flipflopshops.locally.com/hosted/redirect/14484/{store_number}"
            location_name = row["name"]
            street_address = row["address"]
            city = row["city"]
            state = row["state"]
            zip_postal = row["zip"]
            phone = row["phone"]
            country_code = row["country"]
            hoo = ""
            try:
                for key, val in row["display_dow"].items():
                    hoo += val["label"] + ": " + val["bil_hrs"] + ","
            except:
                for val in row["display_dow"]:
                    hoo += val["label"] + ": " + val["bil_hrs"] + ","
            hours_of_operation = hoo.rstrip(",")
            location_type = MISSING
            latitude = row["lat"]
            longitude = row["lng"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
