from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgzip.utils import country_names_by_code
from typing import Iterable, Tuple, Callable
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from fuzzywuzzy import process

logger = SgLogSetup().get_logger("ch")

locator_domain = "https://www.timberland.de"
locator_url = (
    "https://hosted.where2getit.com/timberland/timberlandeu/index_de.newdesign.html"
)
country_url = "https://hosted.where2getit.com/timberland/timberlandeu/rest/getlist?lang=de_DE&like=0.2946610991577996"
json_url = "https://hosted.where2getit.com/timberland/timberlandeu/rest/locatorsearch?like=0.31616223781492603&lang=de_DE"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
}


def determine_country(country):
    Searchable = country_names_by_code()
    resultName = process.extract(country, list(Searchable.values()), limit=1)
    for i in Searchable.items():
        if i[1] == resultName[-1][0]:
            if i[0] == "hk":
                return "cn"
            else:
                return i[0]


class ExampleSearchIteration(SearchIteration):
    def __init__(self, token):
        self._token = token

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        with SgRequests() as http:
            payload = {
                "request": {
                    "appkey": self._token,
                    "formdata": {
                        "geoip": "false",
                        "dataview": "store_default",
                        "atleast": 1,
                        "limit": 250,
                        "geolocs": {
                            "geoloc": [
                                {
                                    "addressline": "seoul",
                                    "country": current_country.upper(),
                                    "latitude": str(coord[0]),
                                    "longitude": str(coord[1]),
                                    "state": "",
                                    "province": "",
                                    "city": "",
                                    "address1": "",
                                    "postalcode": "",
                                }
                            ]
                        },
                        "searchradius": "1000",
                        "radiusuom": "km",
                        "order": "retail_store,outletstore,authorized_reseller,_distance",
                        "where": {
                            "or": {
                                "retail_store": {"eq": ""},
                                "outletstore": {"eq": ""},
                                "icon": {"eq": ""},
                            },
                            "and": {
                                "service_giftcard": {"eq": ""},
                                "service_clickcollect": {"eq": ""},
                                "service_secondchance": {"eq": ""},
                                "service_appointment": {"eq": ""},
                                "service_reserve": {"eq": ""},
                                "service_onlinereturns": {"eq": ""},
                                "service_orderpickup": {"eq": ""},
                                "service_virtualqueuing": {"eq": ""},
                                "service_socialpage": {"eq": ""},
                                "service_eventbrite": {"eq": ""},
                                "service_storeevents": {"eq": ""},
                                "service_whatsapp": {"eq": ""},
                            },
                        },
                        "false": "0",
                    },
                }
            }

            locations = http.post(json_url, headers=headers, json=payload).json()[
                "response"
            ]["collection"]
            if locations:
                found_location_at(coord[0], coord[1])

            logger.info(f"[{current_country}] {coord[0], coord[1]} {len(locations)}")
            for _ in locations:
                location_name = " ".join(
                    bs(_["name"], "lxml").stripped_strings
                ).replace("&reg;", "®")
                if "timberland" not in location_name:
                    continue
                street_address = _["address1"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                if _["address3"]:
                    street_address += " " + _["address3"]
                location_type = "Timberland Outlet"
                if _["retail_store"]:
                    location_type = "Timberland Store"

                hours = _["hours_de"]
                if hours and "Bitte rufen Sie im Ladengesch" in hours:
                    hours = ""
                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url="https://www.timberland.de/utility/handlersuche.html",
                    location_name=location_name,
                    street_address=street_address,
                    city=_.get("city"),
                    state=_.get("state"),
                    zip_postal=_.get("postalcode"),
                    country_code=_.get("country"),
                    store_number=_.get("uid"),
                    phone=_["phone"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    location_type=location_type,
                    hours_of_operation=hours,
                )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(search_type="DynamicGeoSearch")
    with SgRequests(verify_ssl=False) as http:
        token = bs(http.get(locator_url, headers=headers).text, "lxml").select_one(
            "script#brandifyjs"
        )["data-a"]
        payload = {
            "request": {"appkey": token, "formdata": {"objectname": "Account::Country"}}
        }
        countries = []
        for cc in http.post(country_url, headers=headers, json=payload).json()[
            "response"
        ]["collection"]:
            country = determine_country(cc["description"])
            if country == "hk":
                country = "cn"
            if country == "uk":
                country = "gb"
            if country == "xk":
                country = "rs"
            if country in ["ag", "kn", "lc", "vc", ""]:
                country = "pr"
            countries.append(country)
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=150
            )
        ) as writer:
            search_iter = ExampleSearchIteration(token=token)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=countries,
            )

            for rec in par_search.run():
                writer.write_row(rec)
