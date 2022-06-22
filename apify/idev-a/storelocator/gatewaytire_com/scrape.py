from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("gatewaytire")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://gatewaytire.com/"
    base_url = "https://gatewaytire.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=1e323dcfaf&load_all=1&layout=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = bs(_["description_2"], "lxml").a["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            hours = []
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                _hr = sp1.find("b", string=re.compile(r"Hours"))
                if _hr:
                    hours = list(_hr.find_parent("p").stripped_strings)[1:]
            yield SgRecord(
                page_url=page_url,
                store_number=_["title"].split("#")[-1],
                location_name=_["title"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=bs(_["phone"], "lxml").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
