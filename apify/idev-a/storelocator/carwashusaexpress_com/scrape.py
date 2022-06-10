from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson as json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sgpostal.sgpostal import parse_address_intl

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("carwashusaexpress")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://carwashusaexpress.com"
    base_url = "https://carwashusaexpress.com/site-map/"
    with SgRequests() as session:
        links = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find_all("a", string=re.compile(r"^LOCATIONS$"))[1]
            .find_next_sibling("ul")
            .select("li a")
        )
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            location_type = ""
            if sp1.select_one("span.fusion-alert-content"):
                if (
                    "temporarily closed"
                    in sp1.select_one("span.fusion-alert-content").text
                ):
                    location_type = "temporarily closed"
            ss = json.loads(res.split(".fusion_maps(")[1].split(");")[0].strip())
            raw_address = " ".join(
                bs(ss["addresses"][0]["address"], "lxml").stripped_strings
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            temp = []
            _hr = sp1.find("h2", string=re.compile(r"^HOURS OF OPERATION"))
            if not _hr:
                _hr = sp1.find("h2", string=re.compile(r"^HOURS"))
            if _hr:
                for hh in _hr.find_parent().find_next_sibling().select("tr")[1:]:
                    temp.append(": ".join(hh.stripped_strings))
                if not temp:
                    for hh in _hr.find_parent("div").find_next_siblings("div"):
                        if hh.text.strip():
                            temp = hh.stripped_strings
                            break

            for hh in temp:
                dd = [hr.strip() for hr in hh.split() if hr.strip()]
                hours.append(" ".join(dd))

            phone = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = (
                    sp1.find("a", href=re.compile(r"tel:")).text.split(":")[-1].strip()
                ).split(":")[-1]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("h1.entry-title").text.strip(),
                location_type=location_type,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=ss["addresses"][0]["latitude"],
                longitude=ss["addresses"][0]["longitude"],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
