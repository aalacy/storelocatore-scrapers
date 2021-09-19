from typing import Iterable

from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_8
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cardfactory")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.cardfactory.co.uk"
base_url = "https://www.cardfactory.co.uk/on/demandware.store/Sites-cardfactory-UK-Site/default/Stores-FindStores?showMap=true&radius=160.93439999999998&lat={}&long={}"


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    maxZ = search.items_remaining()
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()

        locations = http.get(base_url.format(lat, lng), headers=_headers).json()[
            "stores"
        ]
        logger.info(f"{len(locations)} found")
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(f"[{lat}, {lng}] {progress} [{len(locations)}]")
        for _ in locations:
            hours = []
            for day, hh in _.get("storeHoursJSON", {}).items():
                hours.append(f"{day}: {hh['start']} - {hh['end']}")
            street = _["address1"]
            if _["address2"]:
                street += " " + _["address2"]
            yield SgRecord(
                page_url=base_url,
                store_number=_["ID"],
                location_name=_["name"],
                street_address=street,
                city=_["city"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                zip_postal=_["postalCode"],
                country_code="uk",
                phone=_.get("phone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
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
