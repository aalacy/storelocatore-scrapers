from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pfchangs")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.pfchangs.co.kr"
base_url = "http://www.pfchangs.co.kr/kr/store/list.asp"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.store-list-box li")
        for _ in locations:
            page_url = _.select_one("a.store-view-btn")["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = _.dl.dd.text.strip()
            addr = raw_address.split()
            if addr[0].strip().endswith("도"):
                state = addr[0]
                city = addr[1]
                street_address = " ".join(addr[2:])
            else:
                state = ""
                city = addr[0]
                street_address = " ".join(addr[1:])

            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("=")[-1],
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                country_code="Korea",
                phone=_.select("dl")[1].dd.text.split(":")[-1],
                locator_domain=locator_domain,
                hours_of_operation=sp1.select("dl")[1].dd.text.split("(")[0].strip(),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
