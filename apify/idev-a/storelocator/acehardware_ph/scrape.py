from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://call-collect.acehardware.ph"
base_url = "https://g.smomni.com/graphql"


def fetch_data():
    with SgRequests() as session:
        data = {
            "operationName": "getBranchesByLngLat",
            "variables": {
                "companyId": "5971c431b06bfa0a90c7c3a9",
                "lng": 121.0542674,
                "lat": 14.5834442,
                "distance": 500,
            },
            "query": "query getBranchesByLngLat($companyId: String, $lng: Float, $lat: Float, $distance: Int) {\n  getBranchesByLngLat(companyId: $companyId, lng: $lng, lat: $lat, distance: $distance)\n}\n",
        }
        locations = session.post(base_url, headers=_headers, json=data).json()["data"][
            "getBranchesByLngLat"
        ]
        for _ in locations:
            addr = parse_address_intl(_["address2"] + ", Philippines")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=locator_domain,
                store_number=_["storeCode"],
                location_name=_["name"],
                street_address=street_address.strip(),
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Philippines",
                phone=_["phone"].split(",")[0],
                locator_domain=locator_domain,
                hours_of_operation=_["description"],
                raw_address=_["address2"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
