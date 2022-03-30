from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicZipSearch, Grain_8
from sglogging import SgLogSetup
import re
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("tomford")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tomford.com"
base_url = "https://www.tomford.com/stores"
json_url = "https://www.tomford.com/on/demandware.store/Sites-tomford-Site/default/Stores-GetJSON"


def _d(_, current_country):
    if "TOM FORD" not in _["lines"] and "TOM FORD" not in _["name"]:
        return
    street_address = re.sub("current_country", "", _["address"], flags=re.I)
    if _["city"]:
        street_address = re.sub(_["city"], "", street_address, flags=re.I)
    if _["state"]:
        street_address = re.sub(_["state"], "", street_address, flags=re.I)
    hours = []
    if _["hours"]:
        days = [hh.text.strip() for hh in bs(_["hours"], "lxml").select("dt")]
        times = [hh.text.strip() for hh in bs(_["hours"], "lxml").select("dd")]
        for x in range(len(days)):
            hours.append(f"{days[x]}: {times[x]}")
    return SgRecord(
        page_url="",
        store_number=_["id"],
        location_name=_["name"],
        street_address=street_address,
        city=_["city"],
        state=_["state"],
        zip_postal=_["zip"],
        latitude=_["latLng"][0],
        longitude=_["latLng"][1],
        country_code=current_country,
        phone=_["phone"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def fetch_records(search):
    for zipcode in search:
        with SgRequests() as http:
            url = f"{json_url}?dwfrm_storelocator_address_country=US"
            url += f"&dwfrm_storelocator_postalCode={zipcode}&dwfrm_storelocator_maxdistance=3000.0&dwfrm_storelocator_longitude=&dwfrm_storelocator_latitude="

            locations = http.get(url, headers=_headers).json()
            logger.info(f"[USA] {len(locations)}")
            for _ in locations:
                yield _d(_, "USA")


def record_initial_requests():
    with SgRequests() as http:
        countries = bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "select.country option"
        )
        for country in countries:
            if country["value"] == "US":
                continue
            url = f"{json_url}?dwfrm_storelocator_address_country={country['value']}&dwfrm_storelocator_postalCode=&dwfrm_storelocator_maxdistance=3000.0&dwfrm_storelocator_longitude=&dwfrm_storelocator_latitude="
            locations = http.get(url, headers=_headers).json()
            logger.info(f"[{country['value']}] {len(locations)}")
            for _ in locations:
                yield _d(_, country["value"])


if __name__ == "__main__":
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_8()
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        # Search all countries except for USA
        for rec in record_initial_requests():
            if rec:
                writer.write_row(rec)

        # Search USA
        for rec in fetch_records(search):
            if rec:
                writer.write_row(rec)
