from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgselenium import SgSelenium
import ssl
import time

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


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


def set_cookie(driver):
    cookies = []
    for cookie in driver.get_cookies():
        if cookie["name"] == "dtPC":
            HEADERS["x-dtpc"] = cookie["value"]
        cookies.append(f"{cookie['name']}={cookie['value']}")
    HEADERS["Cookie"] = "; ".join(cookies)
    return True


def get_stores(driver, lat, long, num=0):
    num += 1
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
        + str(HEADERS)
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
    try:
        data = driver.execute_script(script)
        data["data"]["storeList"]
    except:
        if num <= 5:
            log.info("Failed geting store locations, retry for => " + str(num))
            driver.quit()
            driver = SgSelenium().chrome()
            driver.get(BASE_URL)
            set_cookie(driver)
            return get_stores(driver, lat, long, num)
    return driver, data


def get_hoo(days, data):
    hoo = ""
    for i in range(len(days)):
        if data[i]["slots"]:
            if len(data[i]["slots"]) > 1:
                hour = data[i]["slots"]
                hoo += (
                    days[i]
                    + ": "
                    + hour[0]["start_time"]
                    + " - "
                    + hour[0]["end_time"]
                    + " / "
                    + hour[1]["start_time"]
                    + " - "
                    + hour[1]["end_time"]
                    + ","
                )
            else:
                hour = data[i]["slots"][0]
                hoo += (
                    days[i] + ": " + hour["start_time"] + " - " + hour["end_time"] + ","
                )
        else:
            hoo += days[i] + ": Closed,"
    return hoo.strip().rstrip(",")


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(BASE_URL)
    set_cookie(driver)
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
        expected_search_radius_miles=30,
        max_search_results=5,
    )
    coords = [x for x in search]
    coords.append((18.097019874365, -63.042554855347))
    for lat, long in coords:
        driver, data = get_stores(driver, lat, long)
        try:
            data["data"]["storeList"]
        except:
            continue
        for row in data["data"]["storeList"]:
            search.found_location_at(lat, long)
            page_url = BASE_URL + "magasin/" + str(row["id"])
            location_name = row["name"].strip()
            addr = row["address"]
            street_address = " ".join(addr["street"]).strip()
            city = addr["city"].strip()
            state = addr["region"] or MISSING
            zip_postal = addr["postcode"]
            country_code = addr["country_id"]
            phone = row["contact_phone"].strip()
            hours_of_operation = get_hoo(days, row["opening_hours"])
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
        time.sleep(2)
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
