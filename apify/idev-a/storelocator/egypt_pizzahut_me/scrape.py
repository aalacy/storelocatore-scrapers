from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from datetime import datetime
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.egypt.pizzahut.me"
base_url = "https://www.egypt.pizzahut.me/api/stores?deliveryMode=H&langCode=en"


def _t(hh):
    return hh.split(" ")[-1]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["body"]
        for _ in locations:
            hours = []
            for hh in _.get("storeTimings", {}).get("HomeDelivery", []):
                day = datetime.strptime(hh["date"], "%Y-%m-%d").strftime("%A")
                hours.append(f"{day}: {_t(hh['onTime'])} PM - {_t(hh['offTime'])} AM")
            raw_address = f'{_["address"].strip()}, {_["city"]["name"].strip()}, {_["state"]["name"].strip()}, Egypt'
            addr = parse_address_intl(raw_address)
            yield SgRecord(
                page_url="https://www.egypt.pizzahut.me/en/search-location",
                store_number=_["id"],
                location_name=_["name"].strip(),
                street_address=_["address"].strip(),
                city=addr.city,
                state=_["state"]["name"].strip(),
                latitude=_["locationDetail"]["latitude"],
                longitude=_["locationDetail"]["longitude"],
                country_code="Egypt",
                phone=_["contactNo"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
