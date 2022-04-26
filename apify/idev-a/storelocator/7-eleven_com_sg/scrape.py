from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7-eleven.com.sg"
base_url = "https://www.7-eleven.com.sg/Locate"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var servervalue =")[1]
            .split("if (")[0]
            .strip()[1:-2]
            .replace("\\", "/")
        )["location"]
        for _ in locations:
            addr = parse_address_intl(_["locationAddress"] + ", Singapore")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            latitude = _["locationLat"]
            if latitude == "0":
                latitude = ""
            longitude = _["locationLong"]
            if longitude == "0":
                longitude = ""
            yield SgRecord(
                page_url="https://www.7-eleven.com.sg/Locate",
                location_name=_["locationName"],
                street_address=street_address,
                city=addr.city,
                zip_postal=addr.postcode,
                latitude=latitude,
                longitude=longitude,
                country_code="Singapore",
                locator_domain=locator_domain,
                hours_of_operation=_["outlet_open_operating"],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
