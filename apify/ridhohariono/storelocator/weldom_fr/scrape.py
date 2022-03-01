from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgselenium import SgSelenium
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "weldom.fr"
BASE_URL = "https://www.weldom.fr/"
API_URL = "https://www.weldom.fr/graphql"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "content-type": "application/json",
    "origin": BASE_URL,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(BASE_URL)
    cookies = []
    for cookie in driver.get_cookies():
        if cookie["name"] == "dtPC":
            HEADERS["x-dtpc"] = cookie["value"]
        cookies.append(f"{cookie['name']}={cookie['value']}")
    HEADERS["Cookie"] = "; ".join(cookies)
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    driver.implicitly_wait(10)
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.FRANCE],
        max_search_distance_miles=50,
        expected_search_radius_miles=15,
        max_search_results=5,
    )
    for lat, long in search:
        variable = (
            "variables: {gps_coordinate: {latitude: "
            + str(lat)
            + ",longitude: "
            + str(long)
            + ",},},"
        )
        script = (
            """return fetch('https://www.weldom.fr/graphql', {
                method: 'POST',
                headers: """
            + HEADERS
            + """,
                body: JSON.stringify({
                    operationName: "storeList",
                    query: `
                    \n  query storeList($gps_coordinate: GpsCoordinatesFilter) {\n    storeList(gps_coordinate: $gps_coordinate) {\n      id\n      name\n      meta_description\n      meta_title\n      seller_code\n      distance\n      contact_phone\n      url_key\n      address {\n        city\n        latitude\n        longitude\n        country_id\n        postcode\n        region\n        region_id\n        street\n      }\n      image\n      opening_hours {\n        day_of_week\n        slots {\n          start_time\n          end_time\n        }\n      }\n      special_opening_hours {\n        day\n        slots {\n          start_time\n          end_time\n        }\n      }\n      is_available_for_cart\n      ereservation\n      eresa_without_stock\n      online_payment\n      # url_path\n      # type\n      # promotions {\n      #   entity_id\n      #   title\n      #   description\n      #   image\n      #   url\n      #   type\n      # }\n      messages {\n        title\n        message\n        link\n        label_link\n      }\n    }\n  }\n
                `,
                    """
            + variable
            + """
                }),
            }).then((res) => res.json());"""
        )
        log.info(f"Search locations => {lat}, {long}")
        data = driver.execute_script(script)
        for row in data["data"]["storeList"]:
            search.found_location_at(lat, long)
            page_url = BASE_URL + "magasin/" + row["id"]
            location_name = row["name"].strip()
            addr = row["address"]
            street_address = addr["street"].strip()
            city = addr["city"].strip()
            state = addr["region"] or MISSING
            zip_postal = addr["postcode"]
            country_code = addr["country_id"]
            phone = addr["contact_phone"]
            hoo = ""
            for i in range(len(days)):
                hour = row["opening_hours"][i]["slots"][0]
                hoo += (
                    days[i] + ": " + hour["start_time"] + "-" + hour["end_time"] + ","
                )
            hours_of_operation = hoo.strip().rstrip(",")
            store_number = row["id"]
            location_type = MISSING
            latitude = addr["latitude"]
            longitude = addr["longitude"]
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
    driver.quit()


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
