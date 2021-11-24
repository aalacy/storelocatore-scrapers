from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("littlecaesars_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=5,
    max_search_results=1000,
)


def fetch_data():
    for coord in search:
        website = "littlecaesars.com"
        url = "https://api.cloud.littlecaesars.com/bff/api/stores?zip=" + coord
        r = session.get(url, headers=headers)
        try:
            for item in json.loads(r.content)["stores"]:
                name = "Little Caesar's"
                city = item["address"]["city"]
                state = item["address"]["state"]
                country = "US"
                add = item["address"]["street"] + " " + item["address"]["street2"]
                add = add.strip()
                zc = item["address"]["zip"]
                lat = item["latitude"]
                lng = item["longitude"]
                phone = item["phone"]
                store = item["storeId"]
                typ = item["storeType"]
                lnum = item["locationNumber"]
                purl = "https://littlecaesars.com/en-us/store/" + str(lnum)
                try:
                    hours = item["storeOpenTime"] + "-" + item["storeCloseTime"]
                except:
                    hours = "<MISSING>"
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
