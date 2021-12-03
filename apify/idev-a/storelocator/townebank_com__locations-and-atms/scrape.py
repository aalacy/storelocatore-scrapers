from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.townebank.com"
base_url = "https://www.townebank.com/locationapi/getLocations"


def fetch_data(writer):
    with SgRequests() as session:
        data = "atms=true"
        locations = json.loads(
            session.post(base_url, headers=_headers, data=data)
            .text.strip()[1:-1]
            .replace('\\\\"', "'")
            .replace('\\"', '"')
        )
        for _ in locations:
            location_type = ""
            if "not available" in _["notes"]:
                location_type = "branch"
            elif "location only includes an ATM" in _["notes"]:
                location_type = "atm"
            else:
                location_type = "branch, atm"
            page_url = locator_domain + _["url"]
            if _["notes"] and "coming soon" in _["notes"].lower():
                continue
            street_address = _["addressOne"]
            if _["addressTwo"]:
                street_address += " " + _["addressTwo"]
            hours = []
            if _["lobbyHours"]:
                hours = bs(_["lobbyHours"], "lxml").stripped_strings
            rec = SgRecord(
                page_url=page_url,
                store_number=_["nodeId"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["stateDisplayName"],
                zip_postal=_["zipCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phoneNumber"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("\\r", "")
                .replace("\\n", ""),
            )
            writer.write_row(rec)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
