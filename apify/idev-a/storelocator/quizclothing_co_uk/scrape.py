from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch
from sgzip.utils import country_names_by_code
import json
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process

logger = SgLogSetup().get_logger("quizclothing")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.quizclothing.co.uk"
base_url = "https://www.quizclothing.co.uk/google/store-locator"


def determine_country(country):
    Searchable = country_names_by_code()
    resultName = process.extract(country, list(Searchable.values()), limit=1)
    for i in Searchable.items():
        if i[1] == resultName[-1][0]:
            return i[0]


def fetch_records(http, search, country_list):
    for lat, lng in search:
        country = country_list.get(search.current_country())
        url = f"https://www.quizclothing.co.uk/google/store-locator?country={country}&radius=5000&window=&search={lat},{lng}"
        res = http.get(url, headers=_headers).text
        locations = json.loads(
            res.split("$stores =")[1].split("$store_url_suffix")[0].strip()
        )
        logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
        for _ in locations:
            street_address = _["address_1"]
            if _["address_2"]:
                street_address += " " + _["address_1"]
            yield SgRecord(
                page_url=locator_domain + _["url"],
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["town"],
                state=_["country"],
                zip_postal=_["postcode"],
                country_code=_["country"],
                phone=_["telephone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation=_["opening_hours"].replace("\r\n", "; "),
            )


if __name__ == "__main__":
    with SgRequests() as http:
        countries = []
        for country in bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "select#store-locator-country option"
        ):
            countries.append(determine_country(country["value"]))
        search = DynamicGeoSearch(
            country_codes=countries, expected_search_radius_miles=100
        )
        country_list = country_names_by_code()
        with SgWriter(
            deduper=SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(http, search, country_list):
                writer.write_row(rec)
