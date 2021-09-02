from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("guardianhc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://guardianhc.com"
base_url = "https://guardianhc.com/locations/?pg=1"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var locations =")[1]
            .split("var ge_location_search")[0]
            .strip()[:-1]
        )["data"]
        for _ in locations:
            street_address = _["ge_location_street_address"]
            if _["ge_location_street_address_2"]:
                street_address += " " + _["ge_location_street_address_2"]
            sp1 = bs(session.get(_["permalink"], headers=_headers).text, "lxml")
            logger.info(_["permalink"])
            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=_["permalink"],
                store_number=_["ID"],
                location_name=_["post_title"],
                street_address=street_address,
                city=_["ge_location_city"],
                state=_["ge_location_state"],
                zip_postal=_["ge_location_zip_code"],
                latitude=_["ge_location_lat"],
                longitude=_["ge_location_lng"],
                country_code="US",
                phone=phone,
                location_type=_["ge_location_location_type"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
