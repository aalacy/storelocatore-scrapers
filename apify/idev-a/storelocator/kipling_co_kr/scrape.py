from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.co.kr"
base_url = "https://www.kipling.co.kr/stores/info/list"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("li.store-list")
        for _ in locations:
            raw_address = _.select_one("p.address").text.strip()
            addr = raw_address.split()
            state = street_address = city = ""
            if addr[0].endswith("도"):
                state = addr[0]
            if addr[0].endswith("시"):
                city = addr[0]
                street_address = " ".join(addr[1:])
            elif addr[1].endswith("시"):
                city = addr[1]
                street_address = " ".join(addr[2:])
            else:
                street_address = " ".join(addr[1:])

            if "서울" in addr[0] or "대구" in addr[0]:
                city = addr[0]
                street_address = " ".join(addr[1:])

            if "강원" in addr[0]:
                state = "강원"

            coord = (
                _.select_one("a.map-open")["href"].split("||")[-1].strip().split(",")
            )
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_.select_one("strong.store-title").text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                country_code="KR",
                phone=_.select_one("p.telephone").text.strip().split(":")[-1],
                latitude=coord[1],
                longitude=coord[0],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
