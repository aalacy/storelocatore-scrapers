from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://hamleys.ru"
base_url = "https://hamleys.ru/info/shops/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var shopsList =")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )
        for key, locs in locations.items():
            for _ in locs:
                addr = parse_address_intl("Россия, " + _["address"])
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=base_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    latitude=_["gps"]["latitude"],
                    longitude=_["gps"]["longitude"],
                    country_code="Russia",
                    phone=_["phone"].split("доб")[0],
                    locator_domain=locator_domain,
                    hours_of_operation=_["workTime"],
                    raw_address=_["address"],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
