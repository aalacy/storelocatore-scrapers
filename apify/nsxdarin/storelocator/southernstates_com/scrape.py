from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "x-requested-with": "XMLHttpRequest",
}

logger = SgLogSetup().get_logger("southernstates_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=75,
    max_search_results=None,
)


def fetch_data():
    url = "https://www.southernstates.com/api/es/search?pretty"
    for lat, lng in search:
        logger.info(str(lat) + "-" + str(lng))
        payload = {
            "sort": {
                "_geo_distance": {
                    "store.latlong": {"lat": str(lat), "lon": str(lng)},
                    "order": "asc",
                    "unit": "km",
                }
            },
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            "query": "+live:true +(conhost:4ede55af-83ba-47d8-b537-0bca4b7a3058 conhost:SYSTEM_HOST)"
                        }
                    },
                    "filter": [
                        {"term": {"store.webPublish": "1"}},
                        {
                            "geo_distance": {
                                "distance": "75miles",
                                "store.latlong": {"lat": str(lat), "lon": str(lng)},
                            }
                        },
                    ],
                }
            },
            "size": 200,
        }
        r = session.post(url, headers=headers, data=json.dumps(payload))
        array = json.loads(r.content)
        for item in array["contentlets"]:
            website = "southernstates.com"
            store = item["storeNumber"]
            try:
                phone = item["phone"]
            except:
                phone = "<MISSING>"
            city = item["city"]
            state = item["stateAbbr"]
            add = item["address1"]
            try:
                add = add + " " + item["address2"]
            except:
                pass
            add = add.strip()
            name = item["storeNamePublicFacing"]
            lat = item["latlong"].split(",")[0]
            lng = item["latlong"].split(",")[1]
            country = "US"
            typ = "Store"
            zc = item["zipcode"]
            loc = "https://www.southernstates.com/farm-store/store-locations/" + store
            hours = (
                "Mon: "
                + item["storeOpenMonday"].split(" ")[1].rsplit(":", 1)[0]
                + "-"
                + item["storeCloseMonday"].split(" ")[1].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; "
                + "Tue: "
                + item["storeOpenTuesday"].split(" ")[1].rsplit(":", 1)[0]
                + "-"
                + item["storeCloseTuesday"].split(" ")[1].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; "
                + "Wed: "
                + item["storeOpenWednesday"].split(" ")[1].rsplit(":", 1)[0]
                + "-"
                + item["storeCloseWednesday"].split(" ")[1].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; "
                + "Thu: "
                + item["storeOpenThursday"].split(" ")[1].rsplit(":", 1)[0]
                + "-"
                + item["storeCloseThursday"].split(" ")[1].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; "
                + "Fri: "
                + item["storeOpenFriday"].split(" ")[1].rsplit(":", 1)[0]
                + "-"
                + item["storeCloseFriday"].split(" ")[1].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; "
                + "Sat: "
                + item["storeOpenSaturday"].split(" ")[1].rsplit(":", 1)[0]
                + "-"
                + item["storeCloseSaturday"].split(" ")[1].rsplit(":", 1)[0]
            )
            hours = (
                hours
                + "; "
                + "Sun: "
                + item["storeOpenSunday"].split(" ")[1].rsplit(":", 1)[0]
                + "-"
                + item["storeCloseSunday"].split(" ")[1].rsplit(":", 1)[0]
            )
            if phone == "":
                phone = "<MISSING>"
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


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
