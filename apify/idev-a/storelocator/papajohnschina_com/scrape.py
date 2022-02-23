from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.papajohnschina.com"
base_url = "http://www.papajohnschina.com/js/chunk-748cb5cd.98531924.js"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split(",m=")[1]
            .split(",r=[")[0]
            .strip()
        )
        for loc in locations:
            for _ in loc["restaurant"]:
                addr = parse_address_intl("中国" + _["address"])
                state = addr.state
                city = _["address"].split("市")[0]
                if "北京" in city:
                    city = "北京"
                if "天津" in city:
                    city = "天津"
                if "石家庄" in city:
                    city = "石家庄"
                if "昆山" in city:
                    city = "昆山"
                street_address = _["address"].replace(city, "").replace("市", "")
                if state:
                    city = city.split(state)[-1]
                    street_address = street_address.replace(state, "")
                yield SgRecord(
                    location_name=_["name"],
                    street_address=street_address,
                    city=city + "市",
                    state=state,
                    zip_postal=addr.postcode,
                    phone=_.get("phone"),
                    country_code="China",
                    locator_domain=locator_domain,
                    hours_of_operation=_.get("time"),
                    raw_address=_["address"],
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
