from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shell")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shell.ae/"
urls = [
    "https://shelllubricantslocator.geoapp.me/api/v1/global_lubes/locations/nearest_to?lat=24.34785&lng=53.97645&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=47.6942&lng=13.33475&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=50.4957&lng=5.76651&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=12.2359&lng=-1.5662&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=42.73325&lng=25.47425&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=46.81095&lng=8.2107&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=7.61157&lng=-4.00766&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=-36.6114&lng=-71.25915&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=-22.26193&lng=26.59181&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=-1.7257&lng=118.08745&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=0.41114&lng=39.02903&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=13.03745&lng=101.5012&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=1.21809&lng=33.83924&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=-29.0511&lng=30.49292&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=-38.41945&lng=-42.53105&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=-14.23755&lng=-33.3123&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=16.0063&lng=-24.0135&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=18.74165&lng=-70.1692&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=7.94153&lng=1.6283&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=9.9318&lng=-11.37175&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=22.37675&lng=114.28409&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=23.62955&lng=-91.98782&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=4.1036&lng=109.7027&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=12.3748&lng=123.1867&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=30.3745&lng=74.22014&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=60.6838&lng=141.99225&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=1.35645&lng=103.8219&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=38.9593&lng=35.23515&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=49.79895&lng=15.45675&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=51.1682&lng=15.72054&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=65.76673&lng=36.51855&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=47.15525&lng=19.4858&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=21.1205&lng=82.75285&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=49.80815&lng=6.10875&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellretaillocator.geoapp.me/api/v1/locations/nearest_to?lat=28.67325&lng=-9.02285&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellretaillocator.geoapp.me/api/v1/locations/nearest_to?lat=-18.7711&lng=46.8634&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellretaillocator.geoapp.me/api/v1/locations/nearest_to?lat=17.5676&lng=1.25919&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellretaillocator.geoapp.me/api/v1/locations/nearest_to?lat=-20.24835&lng=57.71439&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=52.1528&lng=7.91067&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=64.57925&lng=17.8604&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=51.91615&lng=24.40699&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellfleetlocator.geoapp.me/api/v1/cf/locations/nearest_to?lat=62.18955&lng=17.6358&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&locale=sv_SE&format=json",
    "https://shellfleetlocator.geoapp.me/api/v1/cf/locations/nearest_to?lat=46.1438&lng=14.9403&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&locale=sl_SI&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=48.6759&lng=21.01041&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellretaillocator.geoapp.me/api/v1/locations/nearest_to?lat=14.4985&lng=-13.13854&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=33.78705&lng=12.15867&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=48.37495&lng=31.14615&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
    "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=20.98675&lng=55.9116&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json",
]


def fetch_data():
    with SgRequests() as session:
        for base_url in urls:
            logger.info(base_url)
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                street_address = ""
                if _.get("address"):
                    street_address = _["address"]
                if _.get("address1"):
                    street_address += " " + _["address1"]
                if _.get("address2"):
                    street_address += " " + _["address2"]
                zip_postal = _.get("postcode")
                if zip_postal and zip_postal == "00000":
                    zip_postal = ""
                yield SgRecord(
                    page_url="",
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=_.get("state"),
                    zip_postal=zip_postal,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code=_["country"],
                    phone=_["telephone"],
                    locator_domain=locator_domain,
                    location_type=", ".join(_.get("channel_types", [])),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
