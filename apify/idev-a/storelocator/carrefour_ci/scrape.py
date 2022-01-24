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

locator_domain = "https://www.carrefour.ci"
base_url = "https://www.carrefour.ci/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.malls div.mall")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            location_name = sp1.select_one("h1.page-title").text.strip()
            _hr = sp1.find("strong", string=re.compile(r"^Horaires d’ouverture"))
            hours = ""
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1]
                if hours.startswith(":"):
                    hours = hours[1:]
            _addr = sp1.find("strong", string=re.compile(r"^Adresse du magasin"))
            addr = []
            street_address = city = ""
            if _addr:
                addr = list(_addr.find_parent().stripped_strings)[1:]
                street_address = " ".join(addr[:-1])
                city = addr[-1].split("–")[0].strip().split()[-1].strip()
            phone = ""
            _pp = sp1.find("", string=re.compile(r"Contactez"))
            if _pp:
                phone = (
                    _pp.replace("Contactez", "")
                    .replace("le", "")
                    .split("ou")[0]
                    .strip()
                )
                if phone.startswith(":"):
                    phone = phone[1:]
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                country_code="Ivory Coast",
                phone=phone,
                location_type="Carrefour Market",
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
