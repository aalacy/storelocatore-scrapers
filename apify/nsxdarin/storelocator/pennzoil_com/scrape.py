from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("pennzoil_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=50,
)


def fetch_data():
    for lat, lng in search:
        x = lat
        y = lng
        logger.info(str(x) + "," + str(y))
        website = "pennzoil.com"
        url = (
            "https://locator.pennzoil.com/api/v1/pennzoil/oil_change_locations/nearest_to?limit=50&lat="
            + str(x)
            + "&lng="
            + str(y)
            + "&format=json"
        )
        r = session.get(url, headers=headers)
        purl = "https://www.pennzoil.com/en_ca/oil-change-retail-locations.html"
        for item in json.loads(r.content):
            store = item["id"]
            name = item["name"]
            lat = item["lat"]
            lng = item["lng"]
            add = item["address1"]
            city = item["city"]
            state = item["state"]
            zc = item["postcode"]
            country = "US"
            phone = item["telephone"]
            if phone == "":
                phone = "<MISSING>"
            hours = "<MISSING>"
            typ = "<MISSING>"
            canada = [
                "NL",
                "NS",
                "PE",
                "QC",
                "ON",
                "BC",
                "AB",
                "MB",
                "SK",
                "YT",
                "NU",
                "NT",
                "NB",
            ]
            if state not in canada:
                if "PENNZOIL" in name.upper():
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


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
