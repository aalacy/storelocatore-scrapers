from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("riteaid_com__pharmacy")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}


country = "US"
typ = "Rite-Aid Pharmacy"
website = "riteaid.com/pharmacy"


def fetch_data():
    for lat, lng in search:
        logger.info(f"Querying lat/lng {lat}, {lng}...")
        url = f"https://www.riteaid.com/services/ext/v2/stores/getStores?latitude={lat}&longitude={lng}&radius=10000&pharmacyOnly=true&globalZipCodeRequired=true"
        r = session.get(url, headers=headers)
        stores = r.json()["Data"]["stores"]
        if not stores:
            search.found_nothing()
            continue

        for item in stores:
            store = item["storeNumber"]
            add = item["address"]
            city = item["city"]
            state = item["state"]
            zc = item["zipcode"]
            phone = item["fullPhone"]
            typ = item["storeType"]
            name = "Rite Aid #" + str(store)
            lurl = "https://www.riteaid.com/locations/" + str(store)
            lat = item["latitude"]
            lng = item["longitude"]
            search.found_location_at(lat, lng)
            hours = "Sun: " + item["rxHrsSun"]
            hours = hours + "; Mon: " + item["rxHrsMon"]
            hours = hours + "; Mon: " + item["rxHrsTue"]
            hours = hours + "; Mon: " + item["rxHrsWed"]
            hours = hours + "; Mon: " + item["rxHrsThu"]
            hours = hours + "; Mon: " + item["rxHrsFri"]
            hours = hours + "; Mon: " + item["rxHrsSat"]
            yield SgRecord(
                locator_domain=website,
                page_url=lurl,
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
