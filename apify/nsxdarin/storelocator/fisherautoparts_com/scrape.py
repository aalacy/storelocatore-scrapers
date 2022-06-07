from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("fisherautoparts_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    url = "https://www.fisherautoparts.com/Fisher-Store-Locator.aspx/GetLocations"
    for lat, lng in search:
        x = lat
        y = lng
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        payload = {"lat": str(x), "lng": str(y)}
        r = session.post(url, headers=headers, data=json.dumps(payload))
        for line in r.iter_lines():
            if "DocumentElement" in line:
                items = line.split("\\u003cLocation\\u003e")
                for item in items:
                    if '{"d":' not in item:
                        website = "fisherautoparts.com"
                        name = item.split("\\u003cLocationDesc\\u003e")[1].split("\\")[
                            0
                        ]
                        add = item.split("\\u003cAddress\\u003e")[1].split("\\")[0]
                        try:
                            phone = item.split("Phone\\u003e")[1].split("\\")[0]
                        except:
                            phone = "<MISSING>"
                        hours = "<MISSING>"
                        typ = "Location"
                        city = item.split("CityState\\u003e")[1].split(",")[0]
                        state = (
                            item.split("CityState\\u003e")[1]
                            .split(",")[1]
                            .split("\\")[0]
                            .strip()
                        )
                        zc = "<MISSING>"
                        country = "US"
                        store = item.split("\\u003cLocationId\\u003e")[1].split("\\")[0]
                        lat = item.split("Latitude\\u003e")[1].split("\\")[0]
                        lng = item.split("Longitude\\u003e")[1].split("\\")[0]
                        purl = (
                            "https://www.fisherautoparts.com/Fisher-Store-Locator.aspx"
                        )
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
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
