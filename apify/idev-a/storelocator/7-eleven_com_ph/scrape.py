from typing import Iterable

from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7-eleven.com.ph"
base_url = "https://www.7-eleven.com.ph/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=1000&search_radius=500&autoload=1"


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    for lat, lng in search:
        locations = http.get(base_url.format(lat, lng), headers=_headers).json()
        for _ in locations:
            street_address = _["address"].split("]")[-1]
            if _["address2"]:
                street_address += " " + _["address2"]
            addr = parse_address_intl(street_address + ", Phillipines")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if not street_address:
                street_address = _["address"].split("]")[-1]
            hours = []
            for hh in bs(_["hours"], "lxml").select("tr"):
                hours.append(f"{': '.join(hh.stripped_strings)}")
            yield SgRecord(
                page_url="https://www.7-eleven.com.ph/store-locator/",
                store_number=_["id"],
                location_name=_["store"],
                street_address=street_address.replace("Phillipines", ""),
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Phillipines",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.PHILIPPINES], granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
