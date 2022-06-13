from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dodge_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def parse_hours(json_hours):
    days = [
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ]
    hours = []
    for day in days:
        if json_hours[day]["closed"]:
            hours.append(f"{day}: closed")
        else:
            open_time = (
                json_hours[day]["open"]["time"] + " " + json_hours[day]["open"]["ampm"]
            )
            close_time = (
                json_hours[day]["close"]["time"]
                + " "
                + json_hours[day]["close"]["ampm"]
            )
            hours.append(f"{day}: {open_time}-{close_time}")
    return ", ".join(hours)


def handle_missing(x):
    if not x:
        return "<MISSING>"
    return x


def fetch_data():
    for code in search:
        try:
            logger.info("Pulling Zip Code %s..." % code)
            url = (
                "https://www.dodge.com/bdlws/MDLSDealerLocator?brandCode=D&func=SALES&radius=50&resultsPage=1&resultsPerPage=100&zipCode="
                + code
            )
            r = session.get(url, headers=headers)
            dealers = json.loads(r.content)["dealer"]
            logger.info(f"found {len(dealers)} dealers")
            for dealer in dealers:
                store_number = handle_missing(dealer["dealerCode"])
                website = "dodge.com"
                typ = "<MISSING>"
                name = handle_missing(dealer["dealerName"])
                country = handle_missing(dealer["dealerShowroomCountry"])
                add = handle_missing(dealer["dealerAddress1"])
                add2 = dealer["dealerAddress2"]
                if add2:
                    add = f"add {add2}"
                state = handle_missing(dealer["dealerState"])
                city = handle_missing(dealer["dealerCity"])
                zc = handle_missing(dealer["dealerZipCode"][0:5])
                purl = handle_missing(dealer["website"])
                phone = handle_missing(dealer["phoneNumber"])
                lat = handle_missing(dealer["dealerShowroomLatitude"])
                lng = handle_missing(dealer["dealerShowroomLongitude"])
                hours = parse_hours(dealer["departments"]["sales"]["hours"])
                yield SgRecord(
                    locator_domain=website,
                    page_url=purl,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store_number,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
