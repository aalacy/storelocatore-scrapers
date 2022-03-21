from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

locator_domain = "https://www.dicarlospizza.com"
base_url = "https://cdn5.editmysite.com/app/store/api/v17/editor/users/127469322/sites/289256851898694789/store-locations?page=1&per_page=100&include=address&lang=en&valid=1"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests() as http:
        locations = http.get(base_url, headers=_headers).json()["data"]
        for _ in locations:
            addr = _["address"]["data"]
            street_address = addr["street"]
            if addr["street2"]:
                street_address += " " + addr["street2"]
            page_url = (
                locator_domain
                + f'/{addr["region_code_full_name"].lower().replace(" ", "-")}'
            )
            hours = []
            for hh in json.loads(_["square_business_hours"])["periods"]:
                hours.append(
                    f"{hh['day_of_week']}: {hh['start_local_time']} - {hh['end_local_time']}"
                )
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_address_id"],
                location_name=addr["business_name"],
                street_address=street_address,
                city=addr["city"],
                state=addr["region_code"],
                zip_postal=addr["postal_code"],
                country_code=addr["country_code"],
                phone=addr["phone"],
                latitude=addr["latitude"],
                longitude=addr["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
