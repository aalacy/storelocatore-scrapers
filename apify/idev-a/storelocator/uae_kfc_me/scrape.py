from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://uae.kfc.me"
base_url = (
    "https://uae.kfc.me/Handlers/ItemsInfo.ashx?l=en&isFullData=0&ts=202108111428"
)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers)
        locations = json.loads(
            res.text.split("var OriginalStores=")[1]
            .split("var PhoneMasks")[0]
            .strip()[:-1]
        )
        cities = json.loads(
            res.text.split("var OriginalCities=")[1]
            .split("var OriginalStoreGroupCats")[0]
            .strip()[:-1]
        )
        for key, _ in locations.items():
            if "Test" in _["Name"]:
                continue
            city = cities.get(str(_["CityID"]), {})
            location_name = _["Name"].replace("–", "-")
            hours = []
            for day in days:
                if f"{day}DeliveryStart" in _:
                    start = _[f"{day}DeliveryStart"]
                    end = _[f"{day}DeliveryEnd"]
                    hours.append(f"{day}: {start} - {end}")
            page_url = f"https://uae.kfc.me/#/store/{_['ID']}"
            _addr = _["Address"]
            if "UAE" not in _addr and "United Arab Emirates" not in _addr:
                _addr += ", United Arab Emirates"
            addr = parse_address_intl(
                _addr.replace("-", ",").replace("UAE", "United Arab Emirates")
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if not street_address:
                street_address = _["Address"].strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["ID"],
                location_name=location_name,
                street_address=street_address,
                city=city.get("Name"),
                latitude=_["MapLocation"]["Latitude"],
                longitude=_["MapLocation"]["Longitude"],
                country_code="UAE",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["Address"].strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
