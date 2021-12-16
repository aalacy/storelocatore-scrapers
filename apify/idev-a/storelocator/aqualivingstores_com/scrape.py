from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
import itertools

logger = SgLogSetup().get_logger("aqualivingstores")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://aqualivingstores.com"
base_url = "https://aqualivingstores.com/locations/"


def _p(val):
    if (
        val.replace("(", "")
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


def _addr(_aa):
    addr = list(_aa.find_parent("p").stripped_strings)[1:]
    if not addr:
        addr = [
            list(cc.stripped_strings)
            for cc in _aa.find_parent("p").find_next_siblings("p")
        ]
        addr = list(itertools.chain(*addr))
    return addr[:-1]


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.fusion-builder-row table tr")
        for link in links:
            if not link.select("td")[0].a:
                continue
            location_name = link.a.text.strip()
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _aa = sp1.find("", string=re.compile(r"Address$"))
            addr = []
            if _aa:
                addr = _addr(_aa)
            else:
                _bb = sp1.find("", string=re.compile(r"Outlet Location$"))
                if _bb:
                    addr = _addr(_bb)
                else:
                    _cc = sp1.find("", string=re.compile(r"Outlet$"))
                    if _cc:
                        addr = _addr(_cc)
                    else:
                        temp = [
                            list(aa.stripped_strings)
                            for aa in sp1.select_one(
                                "div.fusion-text.fusion-text-1"
                            ).select("p")[1:]
                        ]
                        for aa in list(itertools.chain(*temp)):
                            _a = aa.lower()
                            if "outlet" in _a or "address" in _a or "location" in _a:
                                continue
                            if _p(aa):
                                continue
                            addr.append(aa)
            _hr = sp1.find("strong", string=re.compile(r"^Hours:"))
            hours = ""
            if _hr:
                _tt = list(_hr.find_parent("p").stripped_strings)
                if len(_tt) == 1:
                    hours = "; ".join(
                        list(_hr.find_parent("p").find_next_sibling().stripped_strings)
                    )
                else:
                    hh = _tt[1]
                    if "by appointment only" in hh or "call for an appointment" in hh:
                        hours = ""
                    elif "seven days a week" in hh:
                        hours = "seven days a week"
                    else:
                        hours = (
                            hh.split("open")[1]
                            .split("Please")[0]
                            .split("Give")[0]
                            .split("To")[0]
                            .split("Call")[0]
                            .replace(".", "")
                            .strip()
                        )
            street_address = city = state = zip_postal = ""
            if len(addr) > 1:
                c_s = [
                    cc.strip()
                    for cc in addr[-1].replace(",", " ").split()
                    if cc.strip()
                ]
                street_address = " ".join(addr[:-1])
                city = " ".join(c_s[:-2])
                state = c_s[-2]
                zip_postal = c_s[-1]
            else:
                city = location_name.split(",")[0].strip()
                state = location_name.split(",")[1].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state.replace(".", ""),
                zip_postal=zip_postal,
                country_code="US",
                phone=link.select("td")[-1].text.strip(),
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
