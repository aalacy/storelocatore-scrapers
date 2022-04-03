from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("walmart_com/fuel")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=None,
)


def fetch_data():
    website = "walmart.com/auto"
    for code in search:
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://www.walmart.com/store/finder/electrode/api/stores?singleLineAddr="
            + code
            + "&distance=50"
        )
        r2 = session.get(url, headers=headers).json()
        if r2["payload"]["nbrOfStores"]:
            if int(r2["payload"]["nbrOfStores"]) > 0:
                for store in r2["payload"]["storesData"]["stores"]:
                    if store["geoPoint"] and "GAS" in str(store):
                        loc = store["detailsPageURL"]
                        snum = store["id"]
                        name = store["displayName"]
                        typ = "Walmart Fuel"
                        add = store["address"]["address"]
                        city = store["address"]["city"]
                        state = store["address"]["state"]
                        zc = store["address"]["postalCode"]
                        phone = store["phone"]
                        country = "US"
                        lat = store["geoPoint"]["latitude"]
                        lng = store["geoPoint"]["longitude"]
                        hours = "<MISSING>"
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
                            store_number=snum,
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

if __name__ == "__main__":
    scrape()
