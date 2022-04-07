from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("harborfreight_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=None,
)


def fetch_data():
    typ = "<MISSING>"
    website = "harborfreight.com"
    for clat, clng in search:
        try:
            logger.info(str(clat) + "-" + str(clng))
            url = (
                "https://api.harborfreight.com/graphql?operationName=FindStoresNearCoordinates&variables=%7B%22filter%22%3A%7B%22status%22%3A%22OPEN%22%7D%2C%22latitude%22%3A"
                + str(clat)
                + "%2C%22longitude%22%3A"
                + str(clng)
                + "%2C%22withDistance%22%3Atrue%7D&extensions=%7B%22persistedQuery%22%3A%7B%22sha256Hash%22%3A%22de67488071fd8519ed17e17001d8aaf81efa1521%22%7D%7D"
            )
            r = session.get(url, headers=headers)
            for item in json.loads(r.content)["data"]["findStoresNearCoordinates"][
                "stores"
            ]:
                store = item["store_number"]
                loc = "https://www.harborfreight.com/storelocator/store?number=" + store
                name = item["title"]
                country = "US"
                add = item["address"]
                city = item["city"]
                state = item["state"]
                zc = item["postcode"]
                phone = item["telephone"]
                lat = item["latitude"]
                lng = item["longitude"]
                hours = (
                    "Mon-Fri: "
                    + item["store_hours_mf"]
                    + "; Sat: "
                    + item["store_hours_sat"]
                    + "; Sun: "
                    + item["store_hours_sun"]
                )
                status = item["status"]
                if status == "NEW" or status == "OPEN":
                    if add == "":
                        add = "<MISSING>"
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
