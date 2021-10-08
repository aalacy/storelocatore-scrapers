from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("littlecaesars")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mexico.littlecaesars.com"
base_url = "https://api.cloud.littlecaesars.com/bff/api/GetClosestStores"


def fetch_data(search, session):
    for zip in search:
        payload = {"address": {"street": "", "city": "", "state": "", "zip": str(zip)}}
        try:
            locations = session.post(base_url, headers=_headers, json=payload).json()[
                "stores"
            ]
            logger.info(f"[{zip}] {len(locations)}")
        except:
            logger.info(f"[{zip}] 0")
            continue
        for _ in locations:
            hours = f"{_['storeOpenTime']} - {_['storeCloseTime']}"
            location_type = ""
            if not _["isOpen"]:
                location_type = "closed"
            addr = _["address"]
            page_url = f"https://mexico.littlecaesars.com/es-mx/order/pickup/stores/{_['franchiseStoreId']}/pickup-time/"
            yield SgRecord(
                page_url=page_url,
                store_number=_["franchiseStoreId"],
                location_name=_["storeName"],
                street_address=addr["street"],
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Mexico",
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as session:
            search = DynamicZipSearch(country_codes=[SearchableCountries.MEXICO])
            results = fetch_data(search, session)
            for rec in results:
                writer.write_row(rec)
