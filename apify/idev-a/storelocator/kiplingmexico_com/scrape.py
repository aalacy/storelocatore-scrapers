from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.kiplingmexico.com",
    "referer": "https://www.kiplingmexico.com/stores",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kiplingmexico.com"
base_url = "https://www.kiplingmexico.com/_v/private/graphql/v1?workspace=master&maxAge=long&appsEtag=remove&domain=store&locale=es-MX"
days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


def fetch_data():
    with SgRequests() as session:
        payload = {
            "operationName": "getStores",
            "variables": {},
            "extensions": {
                "persistedQuery": {
                    "version": "1",
                    "sha256Hash": "471f622bb6d6b106a74e009f2bdd42176342c97f8026842c1d7730bfed53af6d",
                    "sender": "vtex.store-locator@0.x",
                    "provider": "vtex.store-locator@0.x",
                },
                "variables": "eyJmaWx0ZXJCeVRhZyI6Ik1hcmtldHBsYWNlIn0=",
            },
        }
        locations = session.post(base_url, headers=_headers, json=payload).json()[
            "data"
        ]["getStores"]["items"]
        for _ in locations:
            addr = _["address"]
            page_url = f"https://www.kiplingmexico.com/store/{_['name'].lower().replace(' ', '-')}-{addr['state'].lower().replace(' ','-')}-{addr['postalCode']}/{_['id']}"
            hours = []
            for hh in _["businessHours"]:
                hours.append(
                    f"{days[hh['dayOfWeek']]}: {hh['openingTime']} - {hh['closingTime']}"
                )
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=addr["street"],
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["postalCode"],
                country_code="Mexico",
                phone=_["instructions"],
                latitude=addr["location"]["latitude"],
                longitude=addr["location"]["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
