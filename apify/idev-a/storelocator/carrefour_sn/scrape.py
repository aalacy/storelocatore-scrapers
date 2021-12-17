from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("carrefour")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.sn"
base_url = "https://www.carrefour.sn/magasins/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("article.vignette")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            location_name = ""
            if sp1.select_one("h1.page-title"):
                location_name = sp1.select_one("h1.page-title").text.strip()
            _hr = sp1.find("strong", string=re.compile(r"^Horaires d’ouverture"))
            hours = ""
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1]
                if hours.startswith(":"):
                    hours = hours[1:]
            phone = ""
            _pp = sp1.find("", string=re.compile(r"contact au"))
            if _pp:
                phone = _pp.split("contact au")[-1].strip()
                if phone.startswith(":"):
                    phone = phone[1:]
            if not phone:
                _pp = sp1.find("", string=re.compile(r"Nos numéros"))
                if _pp:
                    phone = _pp.find_parent("strong").find_next_sibling().text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                country_code="Senegal",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
