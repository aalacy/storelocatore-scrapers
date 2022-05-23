from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
import itertools
from sgpostal.sgpostal import parse_address_intl

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
    phone = ""
    addr = list(_aa.find_parent("p").stripped_strings)[1:]
    if not addr:
        addr = []
        for cc in _aa.find_parent("p").find_next_siblings("p"):
            if "Hours:" in cc.text:
                break

            addr.append(list(cc.stripped_strings))
        addr = list(itertools.chain(*addr))
    elif _p(addr[-1]):
        phone = addr[-1]
        del addr[-1]

    if not phone:
        pp = (
            _aa.find_parent("p").find("a", href=re.compile(r"tel:"))
            if _aa.find_parent("p")
            else None
        )
        if pp:
            phone = pp.text.strip()
    return addr, phone


def _d(page_url, location_name, raw_address, lat, lng, phone, hours):
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code="US",
        latitude=lat,
        longitude=lng,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours.strip(),
        raw_address=raw_address,
    )


def _latlng(sp1, x):
    lat = lng = ""
    try:
        if sp1.select("div p iframe")[x].get("src"):
            lng, lat = (
                sp1.select("div p iframe")[x]["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3m")[0]
                .split("!3d")
            )
        elif sp1.select("div p iframe")[x].get("nitro-lazy-src"):
            lng, lat = (
                sp1.select("div p iframe")[x]["nitro-lazy-src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3m")[0]
                .split("!3d")
            )
    except:
        pass

    return lat, lng


def _hoo(sp1, x):
    h_br = sp1.find_all("strong", string=re.compile(r"^Hours:"))
    hours = ""
    if h_br:
        _hr = h_br[x]
        _tt = list(_hr.find_parent("p").stripped_strings)
        if len(_tt) == 1:
            temp = []
            for hh in _hr.find_parent("p").find_next_siblings("p"):
                temp.append("; ".join(hh.stripped_strings))
            hours = "; ".join(temp)
        else:
            hh = _tt[1].lower()
            if (
                "by appointment only. please give" in hh
                or "call for an appointment" in hh
            ):
                hours = ""
            elif "seven days a week" in hh:
                hours = "seven days a week"
            else:
                hours = (
                    hh.split("open")[-1]
                    .split("only")[-1]
                    .split("call")[0]
                    .split("give")[0]
                    .replace("please", "")
                    .replace(".", "")
                    .strip()
                )
    else:
        _hr = sp1.find("p", string=re.compile(r"^Hours:"))
        if _hr:
            hours = "; ".join(list(_hr.find_next_sibling().stripped_strings))
    if hours:
        if hours.startswith(","):
            hours = hours[1:]
        if hours.startswith(":"):
            hours = hours[1:]
        if "appointment" in hours:
            hours = ""

    return hours


def _parse_addr(sp1):
    _aa = sp1.find("", string=re.compile(r"Address:?$"))
    phone = ""
    addr = []
    if _aa:
        addr, phone = _addr(_aa)
    else:
        _bb = sp1.find("", string=re.compile(r"Outlet Location$"))
        if _bb:
            addr, phone = _addr(_bb)
        else:
            _cc = sp1.find("", string=re.compile(r"Outlet$"))
            if _cc:
                addr, phone = _addr(_cc)
            else:
                temp = [
                    list(aa.stripped_strings)
                    for aa in sp1.select_one("div.fusion-text.fusion-text-1").select(
                        "p"
                    )[1:]
                ]
                for aa in list(itertools.chain(*temp)):
                    _a = aa.lower()
                    if "outlet" in _a or "address" in _a or "location" in _a:
                        continue
                    if _p(aa):
                        phone = aa
                        continue
                    addr.append(aa)
    if not addr:
        addr = list(sp1.select_one("div.fusion-text.fusion-text-3 p").stripped_strings)
    if addr and "hour" in addr[0].lower():
        if sp1.select_one("div.fusion-text.fusion-text-4"):
            addr = list(
                sp1.select_one("div.fusion-text.fusion-text-4").stripped_strings
            )
    if _p(addr[-1]):
        phone = addr[-1]
        del addr[-1]
    if not phone:
        _pp = sp1.select_one("div.fusion-text.fusion-text-1").find(
            "a", href=re.compile(r"tel:")
        )
        if _pp:
            phone = _pp.text.strip()

    return addr, phone


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = soup.select("a.ccpage_title_link")
        for state in states:
            sp0 = bs(session.get(state["href"], headers=_headers).text, "lxml")
            links = sp0.select("a.ccpage_title_link")
            for link in links:
                location_name = link.text.strip()
                page_url = link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")

                cnt = len(sp1.select("div.fusion-no-small-visibility p iframe"))
                addr, phone = _parse_addr(sp1)
                hours = _hoo(sp1, 0)
                lat, lng = _latlng(sp1, 0)

                yield _d(
                    page_url, location_name, ", ".join(addr), lat, lng, phone, hours
                )
                if cnt > 1:
                    _aa = sp1.find_all("", string=re.compile(r"Address:?$"))[cnt - 1]
                    phone = ""
                    addr = []
                    if _aa:
                        addr, phone = _addr(_aa)
                    hours = _hoo(sp1, 1)
                    lat, lng = _latlng(sp1, 1)

                    yield _d(
                        page_url, location_name, ", ".join(addr), lat, lng, phone, hours
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
