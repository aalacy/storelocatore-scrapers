from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "luckybrand.com"
BASE_URL = "https://www.luckybrand.com"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def get_hours(raw_hours):
    hours = []
    for day in raw_hours.keys():
        if "openIntervals" in raw_hours[day]:
            start = raw_hours[day]["openIntervals"][0]["start"]
            end = raw_hours[day]["openIntervals"][0]["end"]
            hours.append("{}: {}-{}".format(day, start, end))
    return ", ".join(hours)


def fetch_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=500,
        max_search_results=50,
    )
    for lat, lng in search:
        api_url = (
            "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?api_key=0700165de62eb1a445df7d02b02c7831&v=20181201&location="
            + str(lat)
            + ",%20"
            + str(lng)
            + "&limit=50&radius=500&resolvePlaceholders=true&entityTypes=location&savedFilterIds=60879124"
        )
        log.info("Getting stores from => " + api_url)
        json_data = session.get(api_url, headers=HEADERS).json()["response"]["entities"]
        log.info(f"Found {len(json_data)} stores")
        for data in json_data:
            search.found_location_at(lat, lng)
            if "CLOSED" in data["name"]:
                continue
            country_code = data["address"]["countryCode"]
            try:
                page_url = data["websiteUrl"]["url"]
            except KeyError:
                continue
            if "c_pagesName" not in data:
                location_name = MISSING
            else:
                location_name = data["c_pagesName"]
            street_address = data["address"]["line1"]
            if "line2" in data["address"]:
                street_address += " " + str(data["address"]["line2"]).strip()
            city = data["address"]["city"]
            state = data["address"]["region"]
            zip_postal = data["address"]["postalCode"]
            store_number = data["meta"]["id"]
            location_type = data["c_storeType"]
            try:
                hours_of_operation = get_hours(data["hours"])
            except:
                hours_of_operation = MISSING
            phone = data["mainPhone"]
            latitude = data["geocodedCoordinate"]["latitude"]
            longitude = data["geocodedCoordinate"]["longitude"]
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
            RecommendedRecordIds.StoreNumAndPageUrlId,
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
