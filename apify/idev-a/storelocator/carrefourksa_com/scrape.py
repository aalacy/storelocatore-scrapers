from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from typing import Iterable, Tuple, Callable

logger = SgLogSetup().get_logger("carrefourksa")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefourksa.com"
base_url = "{}/en/store-finder?q=&page={}&storeFormat=&latitude={}&longitude={}"
kw_url = "https://www.carrefourkuwait.com/mafkwt/en/store-finder?q=Al%20A%E1%B8%A9mad%C4%AB&page=0&storeFormat="

country_map = {
    "ae": "https://www.carrefourksa.com/mafsau",
    "sa": "https://www.carrefourksa.com/mafsau",
    "jo": "https://www.carrefourjordan.com/mafjor",
    "pk": "https://www.carrefour.pk/mafpak",
}


def _d(_, found_location_at, current_country):
    street_address = _["line1"]
    if _["line2"]:
        street_address += " " + _["line2"]

    state = _.get("state")
    zip_postal = _.get("postalCode")
    raw_address = f"{street_address} {_['town']}"
    if state:
        raw_address += f" {state}"
    if zip_postal:
        raw_address += f" {zip_postal}"
    hours = []
    for day, hh in _["openings"].items():
        hours.append(f"{day}: {hh}")
    city = _["town"]
    if city in [
        "CFC",
        "CoolPoint",
        "Emporium Mall",
        "WTC Mall",
        "Mushroom_Darkstore-GT",
    ]:
        city = ""
    if _["displayName"]:
        location_name = f"{_['displayName']} - {_['town']}"
    else:
        location_name = _["town"]

    found_location_at(_["latitude"], _["longitude"])
    return SgRecord(
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=_.get("state"),
        zip_postal=_.get("postalCode"),
        country_code=current_country,
        phone=_["phone"],
        latitude=_["latitude"],
        longitude=_["longitude"],
        location_type=_["storeFormat"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
        raw_address=raw_address,
    )


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        with SgRequests() as http:

            lat = coord[0]
            lng = coord[1]
            country = country_map.get(current_country)
            page = 0
            while True:
                url = base_url.format(country, page, lat, lng)
                if country == "kw":
                    url = ""
                try:
                    locations = http.get(url, headers=_headers).json()["data"]
                except:
                    locations = []
                    break
                page += 1
                logger.info(
                    f"[{current_country}] [page {page}] [{lat, lng}] {len(locations)}"
                )
                for _ in locations:
                    yield _d(_, found_location_at, current_country)


def fetch_kw():
    with SgRequests() as http:
        locations = http.get(kw_url, headers=_headers).json()["data"]
        for _ in locations:
            yield _d(_, "kw")


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(search_type="DynamicGeoSearch")
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            ),
            duplicate_streak_failure_factor=100,
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=[
                SearchableCountries.KUWAIT,
                SearchableCountries.UNITED_ARAB_EMIRATES,
                SearchableCountries.PAKISTAN,
                SearchableCountries.JORDAN,
                SearchableCountries.SAUDI_ARABIA,
            ],
        )

        for rec in par_search.run():
            writer.write_row(rec)

        recs = fetch_kw()
        for rec in recs:
            writer.write_row(rec)
