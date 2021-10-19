from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("morgenthalfrederics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://morgenthalfrederics.com"
base_url = "https://morgenthalfrederics.com/pages/boutique-locator"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = soup.select(
            "div.shogun-root div.shg-c  div.shg-row div.shg-c-lg-4.shg-c-md-4 div.shg-box-vertical-align-wrapper"
        )
        _state = ""
        for state in states:
            if state.select_one("div.shg-c.Heading"):
                _state = state.select_one("div.shg-c.Heading").text.strip()
            locations = state.select("p")
            for _ in locations:
                if not _.a:
                    continue
                page_url = locator_domain + _.a["href"]
                logger.info(page_url)
                addr = list(_.a.stripped_strings)
                phone = ""
                if _.find("a", href=re.compile(r"tel:")):
                    phone = _.find("a", href=re.compile(r"tel:")).text.strip()
                hours = []
                try:
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    _hr = sp1.find("p", string=re.compile(r"^hours", re.I))
                    if _hr:
                        hours = (
                            _hr.find_parent()
                            .find_parent()
                            .find_next_sibling()
                            .stripped_strings
                        )
                except:
                    pass
                yield SgRecord(
                    page_url=page_url,
                    location_name=addr[0],
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].strip(),
                    state=_state,
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
