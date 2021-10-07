from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, Grain_8
from sgzip.utils import country_names_by_code
from bs4 import BeautifulSoup as bs
from fuzzywuzzy import process

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


def fetch_records(http, search):
    for lat, lng in search:
        url = f"https://www.t2tea.com/on/demandware.store/Sites-UNI-T2-EU-Site/en_{search.current_country().upper()}/Stores-FindStores?radius=1500&lat={lat}&long={lng}&dwfrm_storelocator_latitude={lat}&dwfrm_storelocator_longitude={lng}"
        try:
            res = http.get(url, headers=_headers)
            locations = res.json()["stores"]
        except:
            print(res)
            import pdb

            pdb.set_trace()
        logger.info(url)
        logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
        for _ in locations:
            street_address = _["address1"]
            if _.get("address2"):
                street_address += " " + _["address2"]
            page_url = f"https://www.t2tea.com/en/us/store-locations?storeID={_['ID']}"
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
                hours_of_operation="; ".join(
                    bs(_["storeHours"], "lxml").stripped_strings
                ),
            )


if __name__ == "__main__":
    with SgRequests(
        proxy_country="us", dont_retry_status_codes_exceptions=set([403, 407, 503, 502])
    ) as http:
        countries = []
        for country in bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "ul.location__list-contries li a"
        ):
            countries.append(
                determine_country(country.select_one("span.country-name").text.strip())
            )
        cc = set(countries)
        cc.remove("hk")
        search = DynamicGeoSearch(country_codes=list(cc), granularity=Grain_8())
        country_list = country_names_by_code()
        with SgWriter(
            deduper=SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
