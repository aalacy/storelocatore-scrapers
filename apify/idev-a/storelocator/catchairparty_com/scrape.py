from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("catchairparty")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://catchairparty.com"
base_url = "https://catchairparty.com/locations/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.location_btm")
        logger.info(f"{len(links)} found")
        for link in links:
            if "Coming Soon" in link.h4.text:
                continue
            page_url = link.h4.a["href"]
            if "coming-soon" in page_url:
                continue

            block = list(link.p.stripped_strings)
            if "Coming Soon" in block[0]:
                continue

            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")

            raw_address = ""
            for _addr in list(sp1.select_one("div.about_catch_cnt").stripped_strings):
                if "Location" in _addr:
                    continue

                if _p(_addr):
                    break

                raw_address += " " + _addr

            if "Coming Soon" in raw_address:
                continue

            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            _hr = sp1.find("h2", string=re.compile(r"STORE HOURS"))
            if _hr:
                hours = list(_hr.find_parent().stripped_strings)[1:]
            yield SgRecord(
                page_url=page_url,
                location_name=link.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[1].replace("|", "").strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address.strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
