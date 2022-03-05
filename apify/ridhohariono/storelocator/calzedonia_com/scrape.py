from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "calzedonia.com"
LOCATION_URL = "https://www.calzedonia.com/world/stores/"
API_URL = "https://www.calzedonia.com/on/demandware.store/Sites-calzedonia-ww-Site/en_WS/Stores-FindStores?showMap=true&radius=300&lat={}&long={}&geoloc=true&clzFilter=true&cuoFilter=true&cdoFilter=true"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL,
        max_search_distance_miles=500,
        expected_search_radius_miles=300,
    )
    for lat, lng in search:
        url = API_URL.format(lat, lng)
        try:
            data = session.get(url, headers=HEADERS).json()["stores"]
        except:
            continue
        log.info(f"Found {len(data)} locations from => {url}")
        search.found_location_at(lat, lng)
        for row in data:
            location_name = row["formattedName"].strip()
            if "Coming Soon" in location_name:
                continue
            if row["address2"]:
                street_address = (row["address1"] + ", " + row["address2"]).strip()
            else:
                street_address = row["address1"].strip()
            city = row["city"] or MISSING
            state = MISSING
            zip_postal = row["postalCode"] or MISSING
            if "phone" not in row:
                phone = MISSING
            else:
                phone = row["phone"]
            country_code = row["countryCode"]
            store_number = row["ID"]
            hoo = ""
            try:
                for hday in row["storeHours"]:
                    day = hday["name"]
                    hours = hday["phases"]
                    if len(hours.strip()) == 0:
                        hours = "CLOSED"
                    hoo += day + ": " + hours + ","
                hours_of_operation = hoo.rstrip(",")
            except:
                hours_of_operation = MISSING
            latitude = row["latitude"]
            longitude = row["longitude"]
            location_type = MISSING
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            ),
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
