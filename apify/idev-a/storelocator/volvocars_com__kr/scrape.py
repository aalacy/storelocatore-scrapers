from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/kr"
base_url = "https://vckiframe.com/oxp/center/json/showroom.json?ver=20210621-01"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            hours = [bs(_["time_1"], "lxml").text.strip()]
            hours += [bs(_["time_2"], "lxml").text.strip()]
            raw_address = bs(_["addr"], "lxml").text.strip()
            addr = [aa.strip() for aa in raw_address.split() if aa.strip()]
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
            else:
                street_address = " ".join(addr[1:])
            yield SgRecord(
                page_url=_["site"],
                store_number=_["zindex"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=state,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="KR",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
