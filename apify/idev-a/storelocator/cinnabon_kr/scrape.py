from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cinnabon")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.cinnabon.kr"
base_url = "https://www.cinnabon.kr/87/?sort=TIME&keyword_type=all&page={}"
json_url = "https://www.cinnabon.kr/ajax/map_more_view.cm"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            sp1 = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            last_page = sp1.select("ul.pagination li")[-2].text
            if page > int(last_page):
                break
            links = sp1.select("div.map-list-detail div.map_container")
            logger.info(f"[page {page}] {len(links)} found")
            for link in links:
                if link.img and link.img["src"].endswith(".png"):
                    continue
                back_url = base_url.format(page).split(locator_domain)[-1]
                idx = link["id"].split("_")[-1]
                data = {
                    "idx": idx,
                    "code": link["data-bcode"],
                    "back_url": f"{back_url}#/map{idx}",
                    "update_time": "N",
                }
                _ = session.post(json_url, headers=_headers, data=data).json()["data"]
                addr = _["address"].split()
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
                else:
                    street_address = " ".join(addr[1:])
                page_url = base_url.format(page) + f"#/map{_['idx']}"
                logger.info(page_url)
                info = bs(_["body"], "lxml")
                _hr = info.find("span", string=re.compile(r"운영시"))
                hours = []
                if _hr:
                    hours = [
                        hh.text.strip()
                        for hh in _hr.find_parent().find_next_siblings("p")
                        if hh.text.strip()
                    ]
                latitude = _["pos_y"]
                longitude = _["pos_x"]
                if latitude == "0":
                    latitude = ""
                if longitude == "0":
                    longitude = ""
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["idx"],
                    location_name=_["subject"],
                    street_address=street_address,
                    city=city,
                    state=state,
                    latitude=latitude,
                    longitude=longitude,
                    country_code="Korea",
                    phone=_.get("phone_number"),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=_["address"],
                )

            page += 1


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
