from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cinnabon.cl"
base_url = "https://api.getjusto.com/graphql?operationName=getStoresZones"


def fetch_data():
    with SgRequests() as session:
        payload = {
            "operationName": "getStoresZones",
            "variables": {"websiteId": "FAp6aFgLpxD8mty8Q"},
            "query": "query getStoresZones($websiteId: ID) {\n  stores(websiteId: $websiteId) {\n    items {\n      _id\n      name\n      phone\n      humanSchedule {\n        days\n        schedule\n        __typename\n      }\n      acceptDelivery\n      acceptGo\n      zones {\n        _id\n        deliveryLimits\n        __typename\n      }\n      address {\n        placeId\n        location\n        address\n        addressSecondary\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        }
        locations = session.post(base_url, headers=_headers, json=payload).json()[
            "data"
        ]["stores"]["items"]
        for _ in locations:
            _addr = _["address"]
            street_address = _addr["address"]
            if street_address == "undefined":
                street_address = ""
            raw_address = street_address + " " + _addr["addressSecondary"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            for hh in _.get("humanSchedule", []):
                hours.append(f"{hh['days']}: {hh['schedule']}")
            yield SgRecord(
                page_url="https://www.cinnabon.cl/local",
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_addr["location"]["lat"],
                longitude=_addr["location"]["lng"],
                country_code="Chile",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
