from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://thegreatmaple.com/"
base_url = "https://thegreatmaple.com/"


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
        locations = soup.select("div.menu ul li ul")[0].select("li a")
        for link in locations:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _ad = sp1.find("", string=re.compile(r"^ADDRESS"))
            _parent = None
            if _ad.find_parent("h3"):
                _parent = _ad.find_parent("h3")
            elif _ad.find_parent("h4"):
                _parent = _ad.find_parent("h4")
            elif _ad.find_parent("h5"):
                _parent = _ad.find_parent("h5")
            addr = list(_parent.find_next_sibling().stripped_strings)
            if not addr[0].split()[0].isdigit():
                del addr[0]

            phone = ""
            if _p(addr[-1]):
                phone = addr[-1]
                del addr[-1]

            _hr = sp1.find("", string=re.compile(r"^HOURS"))
            hours = []
            if _hr.find_parent("h3"):
                tt = _hr.find_parent("h3").find_next_siblings()
            elif _hr.find_parent("h4"):
                tt = _hr.find_parent("h4").find_next_siblings()
            elif _hr.find_parent("h5"):
                tt = _hr.find_parent("h5").find_next_siblings()

            for hh in tt:
                if not hh.text.strip():
                    continue
                if hh.span and hh.span.strong:
                    hours.append(hh.text.strip())
                elif hh.strong or hh.b:
                    temp = list(hh.stripped_strings)
                    if "Hour" in temp[-1]:
                        del temp[-1]
                    for x in range(0, len(temp), 2):
                        hours.append(f"{temp[x]} {temp[x+1]}")
                else:
                    for hr in hh.stripped_strings:
                        if "Hour" in hr:
                            break
                        hours.append(hr)
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
