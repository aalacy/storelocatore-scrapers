from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jambajuice")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://jambajuice.co.kr"
base_url = "https://jambajuice.co.kr/stores"


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


def _d(_, page_url):
    block = _.select("div.storeinfo ul li")
    _addr = list(block[1].select_one("p.detail").stripped_strings)

    phone = ""
    if _p(_addr[-1]):
        phone = _addr[-1]
        del _addr[-1]
    addr = [aa.strip() for aa in " ".join(_addr).split() if aa.strip()]
    state = street_address = city = ""
    if addr[0].endswith("도"):
        state = addr[0]
    if addr[0].endswith("시"):
        city = addr[0]
        street_address = " ".join(addr[1:])
    elif addr[1].endswith("시"):
        city = addr[1]
        street_address = " ".join(addr[2:])
    elif "인천" in addr[0]:
        city = "인천"
        street_address = " ".join(addr[1:])
    elif "서울" in addr[0]:
        city = "서울"
        street_address = " ".join(addr[1:])
    elif "부산" in addr[0]:
        city = "부산"
        street_address = " ".join(addr[1:])
    elif "경기" in addr[0]:
        state = "경기"
        street_address = " ".join(addr[1:])
    else:
        street_address = " ".join(addr[1:])
    return SgRecord(
        page_url=page_url,
        location_name=_.select_one("p.storetit").text.strip(),
        street_address=street_address,
        city=city,
        state=state,
        country_code="KR",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=block[0].select_one("p.detail").text.split("(")[0].strip(),
        raw_address=" ".join(addr),
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.store2dpth ul li a")
        for loc in locations:
            page_url = locator_domain + loc["href"]
            logger.info(page_url)
            _ = bs(session.get(page_url, headers=_headers).text, "lxml")
            yield _d(_, page_url)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
