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
    "franchiseid": "3",
    "latitude": "",
    "longitude": "",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.qatar.pizzahut.me"
base_url = "https://www.qatar.pizzahut.me/api/stores"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Data"]
        for _ in locations:
            hours = []
            if _["operatinghours"]:
                for hh in _.get("operatinghours", []):
                    hr = f"{hh['day']}: {hh['start_time']}-{hh['close_time']}"
                    if hr not in hours:
                        hours.append(hr)
            yield SgRecord(
                page_url="https://www.qatar.pizzahut.me/huts/en",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=_["address1"],
                city=_["city"],
                state=_["state"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Qatar",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
