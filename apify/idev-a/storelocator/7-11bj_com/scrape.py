from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup
from urllib.parse import urljoin

logger = SgLogSetup().get_logger("7-11bj")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.7-11bj.com"
base_url = "http://www.7-11bj.com/?store.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        areas = soup.select("div.shopList a")
        for link in areas:
            url = urljoin(locator_domain, link["href"])
            locations = bs(session.get(url, headers=_headers).text, "lxml").select(
                "div.storeTbl table tr"
            )
            for _ in locations:
                page_url = urljoin(locator_domain, _.a["href"])
                res = session.get(page_url, headers=_headers).text
                sp1 = bs(res, "lxml")
                logger.info(page_url)
                tr = sp1.select("div.storeTbl table tr")
                raw_address = tr[0].td.text.strip()
                addr = parse_address_intl("中国" + raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                try:
                    coord = res.split("new BMap.Point(")[1].split(")")[0].split(",")
                    if len(coord) == 1:
                        coord = ["", ""]
                except:
                    coord = ["", ""]
                yield SgRecord(
                    page_url=page_url,
                    store_number=page_url.split("/")[-1].split(".")[0],
                    location_name=_.a.text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=tr[1].td.text.strip(),
                    country_code="China",
                    phone=tr[2].td.text.strip(),
                    latitude=coord[1],
                    longitude=coord[0],
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
