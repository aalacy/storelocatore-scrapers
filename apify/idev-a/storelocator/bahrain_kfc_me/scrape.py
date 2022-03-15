from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bahrain.kfc.me"
base_url = (
    "https://bahrain.kfc.me/Handlers/ItemsInfo.ashx?l=en&isFullData=0&ts=202107281529"
)


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var OriginalStores=")[1]
            .split(";var PhoneMasks")[0]
        )
        for store_number, _ in locations.items():
            _addr = _["Address"]
            if "bahrain" not in _addr.lower():
                _addr += ", Bahrain"
            addr = parse_address_intl(_addr)
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = f"{_['workHourStart']} - {_['workHourEnd']}"
            page_url = f"https://bahrain.kfc.me/#/store/{store_number}"
            city = addr.city
            if city:
                city = city.replace("Road44", "").replace("Road1315", "")
            latitude = _["MapLocation"]["Latitude"]
            if latitude == 0:
                latitude = ""
            longitude = _["MapLocation"]["Longitude"]
            if longitude == 0:
                longitude = ""
            yield SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=_["Name"],
                street_address=street_address.replace("Bahrain", ""),
                city=city,
                state=addr.state,
                latitude=latitude,
                longitude=longitude,
                country_code="Bahrain",
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=_["Address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
