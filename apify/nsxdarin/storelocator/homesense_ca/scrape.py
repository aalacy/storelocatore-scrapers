from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
}

logger = SgLogSetup().get_logger("homesense_ca")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=50,
    max_search_results=25,
)


def fetch_data():
    for lat, lng in search:
        try:
            logger.info(str(lat) + ", " + str(lng))
            url = "https://marketingsl.tjx.com/storelocator/GetSearchResults"
            payload = {
                "chain": 90,
                "geolat": lat,
                "geolong": lng,
                "lang": "en",
                "maxstores": 25,
            }
            r = session.post(url, headers=headers, data=payload)
            website = "homesense.ca"
            typ = "<MISSING>"
            country = "CA"
            logger.info("Pulling Stores")
            for item in json.loads(r.content)["Stores"]:
                add = item["Address"]
                try:
                    add = add + " " + item["Address2"]
                except:
                    pass
                add = add.strip()
                city = item["City"]
                hours = item["Hours"]
                lat = item["Latitude"]
                lng = item["Longitude"]
                loc = "<MISSING>"
                name = item["Name"]
                phone = item["Phone"]
                state = item["State"]
                zc = item["Zip"]
                store = item["StoreID"]
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
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
