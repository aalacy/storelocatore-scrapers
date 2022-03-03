from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("whittard")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.whittard.co.uk"
base_url = "https://www.whittard.co.uk/on/demandware.store/Sites-WhittardUK-Site/en_GB/Stores-FindStores?dwfrm_storelocator_search=search&format=ajax&lat={}&lng=-{}"


def fetch_records(http, search):
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
            _addr = list(_.select_one("div.store-details").stripped_strings)
            raw_address = ", ".join(_addr)
            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address.isdigit() or len(street_address.split()) == 2:
                street_address = _addr[0]
            hours = []
            for hh in _.select("div.store-hours div.store-content > div"):
                cell = hh.select("div.cell")
                if not cell:
                    hours = [hh.text.strip()]
                else:
                    times = "closed"
                    if len(cell) > 1:
                        times = cell[1].text.strip()
                        if not times:
                            times = "closed"
                    hours.append(f"{cell[0].text.strip()}: {times}")
            yield SgRecord(
                page_url=_.select_one("a.store-details-link")["href"],
                store_number=_["data-storeid"],
                location_name=_.select_one("span.store-header").text.strip(),
                street_address=street_address,
                city=_addr[-2],
                zip_postal=_addr[-1],
                country_code="GB",
                phone=list(_.select_one("div.contacts-desktop").stripped_strings)[-1],
                latitude=_.select_one("span.store-header")["data-lat"],
                longitude=_.select_one("span.store-header")["data-lng"],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
                raw_address=raw_address,
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
