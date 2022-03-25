from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("t-mobile_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=None,
)

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authority": "www.t-mobile.com",
    "accept": "application/json, text/plain, */*",
    "clientapplicationid": "OCNATIVEAPP",
    "loginin": "mytest016@outlook.com",
    "locale": "en_US",
}


def parse_hours(store):
    if "standardHours" not in store or not store["standardHours"]:
        return "<MISSING>"
    hours = []
    days = store["standardHours"]
    for day in days:
        if "opens" in day:
            hours.append("{}: {}-{}".format(day["day"], day["opens"], day["closes"]))
    return ", ".join(hours)


def compute_location_type(store):
    statusDefinition = store["storeDefinition"]
    deviceRepair = store["deviceRepair"]
    hasSprintStack = store["hasSprintStack"]
    hasTmobileStack = store["hasTmobileStack"]
    tags = store["storeTag"]
    if (
        statusDefinition is None
        and hasSprintStack is False
        and hasTmobileStack is False
    ):
        return "T-Mobile Authorized Dealer"
    elif "signature" in tags:
        return "T-Mobile Signature Store"
    elif hasSprintStack is True and hasTmobileStack is False:
        return "Sprint Store"
    elif (
        deviceRepair is False and hasTmobileStack is True and "FPR" in statusDefinition
    ):
        return "T-Mobile Store"
    elif deviceRepair is False and "TPR" in statusDefinition:
        return "T-Mobile Authorized Retailer"
    elif (
        deviceRepair is True
        and hasSprintStack is True
        and hasTmobileStack is True
        and "FPR" in statusDefinition
    ):
        return "T-Mobile Store (Sprint Repair Center)"
    else:
        return "T-Mobile Store"


def handle_missing(x):
    if not x or not x.strip():
        return "<MISSING>"
    return x


def fetch_data():
    for llat, llng in search:
        url = (
            "https://onmyj41p3c.execute-api.us-west-2.amazonaws.com/prod/v2.1/getStoresByCoordinates?latitude="
            + str(llat)
            + "&longitude="
            + str(llng)
            + "&count=50&radius=100&ignoreLoadingBar=false"
        )
        try:
            stores = session.get(url, headers=headers).json()
            website = "t-mobile.com"
            if "code" not in stores:
                for store in stores:
                    if "name" in store:
                        name = store["name"]
                    else:
                        name = "<MISSING>"
                    store = store["id"]
                    typ = compute_location_type(store)
                    if "url" in store:
                        loc = store["url"]
                    else:
                        loc = "<MISSING>"
                    phone = handle_missing(store["telephone"])
                    location = store["location"]
                    address = location["address"]
                    add = handle_missing(address["streetAddress"])
                    city = handle_missing(address["addressLocality"])
                    state = handle_missing(address["addressRegion"])
                    zc = handle_missing(address["postalCode"])
                    country = "US"
                    lat = location["latitude"]
                    lng = location["longitude"]
                    hours = parse_hours(store)
                    yield SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        phone=phone,
                        location_type=typ,
                        store_number=store,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                    )
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
