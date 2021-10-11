from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from typing import Iterable

logger = SgLogSetup().get_logger("whittard")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.whittard.co.uk"
base_url = "https://www.whittard.co.uk/on/demandware.store/Sites-WhittardUK-Site/en_GB/Stores-FindStores?dwfrm_storelocator_search=search&format=ajax&lat={}&lng=-{}"


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    maxZ = search.items_remaining()
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()

        locations = bs(
            http.get(base_url.format(lat, lng), headers=_headers).text, "lxml"
        ).select("div.store-row-container div.store-row")
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(f"{lat}, {lng} {progress} [{len(locations)}]")
        for _ in locations:
            addr = list(_.select_one("div.store-details").stripped_strings)
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in _.select("div.store-hours div.store-content > div")
            ]
            yield SgRecord(
                page_url=_.select_one("a.store-details-link")["href"],
                store_number=_["data-storeid"],
                location_name=_.select_one("span.store-header").text.strip(),
                street_address=addr[0].replace(",", " ").strip(),
                city=addr[1],
                zip_postal=addr[-1],
                country_code="GB",
                phone=list(_.select_one("div.contacts-desktop").stripped_strings)[-1],
                latitude=_.select_one("span.store-header")["data-lat"],
                longitude=_.select_one("span.store-header")["data-lng"],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
