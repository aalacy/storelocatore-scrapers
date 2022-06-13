from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("huntington_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=10,
)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}


def fetch_data():
    for lat, lng in search:
        try:
            x = lat
            y = lng
            url = "https://www.huntington.com/post/GetLocations/GetLocationsList"
            payload = {
                "longitude": y,
                "latitude": x,
                "typeFilter": "1",
                "envelopeFreeDepositsFilter": False,
                "timeZoneOffset": "300",
                "scController": "GetLocations",
                "scAction": "GetLocationsList",
            }
            logger.info("%s - %s..." % (str(x), str(y)))
            session = SgRequests()
            r = session.post(url, headers=headers, data=payload)
            for item in json.loads(r.content)["features"]:
                store = item["properties"]["LocID"]
                name = item["properties"]["LocName"]
                add = item["properties"]["LocStreet"]
                phone = item["properties"]["LocPhone"]
                city = item["properties"]["LocCity"]
                state = item["properties"]["LocState"]
                zc = item["properties"]["LocZip"]
                typ = "<MISSING>"
                website = "huntington.com"
                country = "US"
                flng = item["geometry"]["coordinates"][0]
                flat = item["geometry"]["coordinates"][1]
                try:
                    hours = "Sun: " + item["properties"]["SundayLobbyHours"]
                    hours = hours + "; Mon: " + item["properties"]["MondayLobbyHours"]
                    hours = hours + "; Tue: " + item["properties"]["TuesdayLobbyHours"]
                    hours = (
                        hours + "; Wed: " + item["properties"]["WednesdayLobbyHours"]
                    )
                    hours = hours + "; Thu: " + item["properties"]["ThursdayLobbyHours"]
                    hours = hours + "; Fri: " + item["properties"]["FridayLobbyHours"]
                    hours = hours + "; Sat: " + item["properties"]["SaturdayLobbyHours"]
                except:
                    hours = "<MISSING>"
                loc = (
                    "https://www.huntington.com/Community/branch-info?locationId="
                    + store.replace("bko", "")
                )
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
                    latitude=flat,
                    longitude=flng,
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
