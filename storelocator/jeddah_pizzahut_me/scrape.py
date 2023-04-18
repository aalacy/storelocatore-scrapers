from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "franchiseid": "4",
    "latitude": "",
    "longitude": "",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://jeddah.pizzahut.me/"
base_url = "https://pizzahutsaudiarabia.suntechsolutions.us/api/stores"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Data"]
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            for hh in _.get("operatinghours", []):
                hours.append(f"{hh['day']}: {hh['start_time']} - {hh['close_time']}")
            yield SgRecord(
                page_url="https://jeddah.pizzahut.me/huts/en",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                phone=_["phone"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Saudi Arabia",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
