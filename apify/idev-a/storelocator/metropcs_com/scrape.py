from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.metrobyt-mobile.com"
base_url = "https://www.metrobyt-mobile.com/self-service-sigma-commerce/v1/store-locator?address=&store-type=All&min-latitude={}&max-latitude={}&min-longitude={}&max-longitude={}"


def fetch_data(search):
    for lat, lng in search:
        max_lat = lat + 0.579710145
        max_lng = lng - 0.754716981
        with SgRequests() as session:
            res = session.get(
                base_url.format(lat, max_lat, lng, max_lng), headers=_headers
            )
            if res.status_code != 200:
                continue
            locations = res.json()
            if locations:
                search.found_location_at(lat, lng)
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                addr = _["location"]["address"]
                page_url = f"https://www.metrobyt-mobile.com/storelocator/{addr['addressRegion'].lower()}/{addr['addressLocality'].lower().replace(' ', '-')}/{addr['streetAddress'].lower().replace(' ', '-')}"
                hours = []
                for hh in _["openingHours"]:
                    hours.append(f'{",".join(hh["days"])}: {hh["time"]}')
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=addr["streetAddress"],
                    city=addr["addressLocality"],
                    state=addr["addressRegion"],
                    zip_postal=addr["postalCode"],
                    latitude=_["location"]["latitude"],
                    longitude=_["location"]["longitude"],
                    country_code="US",
                    phone=_["telephone"],
                    location_type=_["type"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
