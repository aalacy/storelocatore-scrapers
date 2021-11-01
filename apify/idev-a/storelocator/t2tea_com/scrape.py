from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch
from sgzip.utils import country_names_by_code
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process
import httpx

timeout = httpx.Timeout(5.0)
logger = SgLogSetup().get_logger("t2tea")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.t2tea.com"
base_url = "https://www.t2tea.com/en/us/home"


def determine_country(country):
    Searchable = country_names_by_code()
    resultName = process.extract(country, list(Searchable.values()), limit=1)
    for i in Searchable.items():
        if i[1] == resultName[-1][0]:
            return i[0]


def fetch_records(http, search, country_map):
    current_country = search.current_country()
    cc = country_map[current_country]
    for lat, lng in search:
        url = f"https://www.t2tea.com/on/demandware.store/{cc[0]}/{cc[1]}/Stores-FindStores?radius=1500&lat={lat}&long={lng}&dwfrm_storelocator_latitude={lat}&dwfrm_storelocator_longitude={lng}"
        logger.info(f"[{current_country}] {lat, lng}")
        res = http.get(url, headers=_headers)
        locations = res.json()["stores"]
        logger.info(f"{len(locations)} found")
        if locations:
            search.found_location_at(lat, lng)
        for _ in locations:
            street_address = _["address1"]
            if _.get("address2"):
                street_address += " " + _["address2"]
            page_url = f"https://www.t2tea.com/en/us/store-locations?storeID={_['ID']}"
            hours = []
            if _["storeHours"]:
                hours = bs(_["storeHours"], "lxml").stripped_strings
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["ID"],
                street_address=street_address,
                city=_["city"],
                state=_.get("stateCode").replace(".", ""),
                zip_postal=_.get("postalCode"),
                country_code=_["countryCode"],
                phone=_.get("phone"),
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgRequests(timeout_config=timeout) as http:
        countries = []
        country_map = {}
        logger.info("... read countries")
        for country in bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "ul.location__list-contries li a"
        ):
            cc = country.select_one("span.country-name").text.strip()
            if cc == "Hong Kong":
                continue
            d_cc = determine_country(cc)
            countries.append(d_cc)
            cn = country["data-deliver-to-country"].lower()
            logger.info(country["href"])
            link = bs(
                http.get(country["href"], headers=_headers).text, "lxml"
            ).select_one("div.select-country__default-contries")["data-url"]
            com1 = link.split("demandware.store/")[1].split("/")[0]
            com2 = country["data-locale"]
            country_map[d_cc] = [com1, com2]
        search = DynamicGeoSearch(
            country_codes=list(set(countries)),
        )
        logger.info("... search")
        with SgWriter(
            deduper=SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
            )
        ) as writer:
            with SgRequests(proxy_country="us", verify_ssl=False) as http:
                for rec in fetch_records(http, search, country_map):
                    writer.write_row(rec)
