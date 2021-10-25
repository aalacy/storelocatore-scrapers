from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson as json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("take5carwash")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.take5carwash.com"
    base_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/12419/stores.js?callback=SMcallback2"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("SMcallback2(")[1]
            .strip()[:-1]
        )["stores"]
        for _ in locations:
            raw_address = _["address"]
            addr = raw_address.split(",")
            hours = []
            if _["description"]:
                for hh in bs(_["description"], "lxml").stripped_strings:
                    if "wash" in hh.lower() or "our" in hh.lower():
                        break
                    hours.append(hh)
            state = addr[-1].strip().split()[0]
            if state.isdigit():
                state = ""
            page_url = _["url"]
            if not state:
                res = session.get(page_url, headers=_headers).text
                ss = json.loads(res.split(".fusion_maps(")[1].split(");")[0].strip())
                raw_address = " ".join(
                    bs(ss["addresses"][0]["address"], "lxml").stripped_strings
                )
                state = parse_address_intl(raw_address).state
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=" ".join(addr[:-2]),
                city=addr[-2],
                state=state,
                zip_postal=addr[-1].strip().split()[-1],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
