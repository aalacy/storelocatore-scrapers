from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ptandrehab.urpt.com"
base_url = (
    "https://ptandrehab.urpt.com/find-a-location/?state=MI&brand=&zip=&all-brands=0"
)


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var locations =")[1]
            .split("var")[0]
            .strip()[:-1]
        )
        for _ in locations:
            if _["is_coming_soon"] != "0":
                continue
            logger.info(_["href"])
            sp1 = bs(session.get(_["href"], headers=_headers).text, "lxml")
            _hr = sp1.find("p", string=re.compile(r"HOURS:"))
            hours = ""
            if _hr:
                hours = _hr.find_parent().find_next_sibling().text.strip()
            yield SgRecord(
                page_url=_["href"],
                store_number=_["id"],
                location_name=" ".join(_["name"]),
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
