from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.spar.com.au"
base_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/4519/stores.js?callback=SMcallback2"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("SMcallback2(")[1]
            .strip()[:-1]
        )["stores"]
        for _ in locations:
            _addr = [aa.strip() for aa in _["address"].split(",")]
            street_address = city = state = zip_postal = ""
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_postal = addr.postcode
            if _addr[-1].isdigit():
                zip_postal = _addr[-1]
                if not state and len(_addr[-2]) == 3:
                    state = _addr[-2]
                if not city:
                    city = _addr[-3]
                    if "Avenue" in city or "Street" in city:
                        city = ""
            if city and city.lower() in _["address"].lower():
                reg1 = r","
                reg2 = r"[\s]?"
                street_address = [
                    aa.strip()
                    for aa in re.split(
                        re.compile(f"{city}{reg2}{reg1}", re.I), _["address"]
                    )
                    if aa.strip()
                ][0].strip()
                if street_address.endswith(","):
                    street_address = street_address[:-1]

            yield SgRecord(
                page_url="https://www.spar.com.au/locations",
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="AU",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=_["custom_field_1"]
                .replace(",", ";")
                .split("(")[0]
                .strip(),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
