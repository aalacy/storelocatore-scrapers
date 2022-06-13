from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.psychobunny.jp"
base_url = "https://www.psychobunny.jp/shoplist/"
prefecture_url = "https://en.wikipedia.org/wiki/Prefectures_of_Japan"


def fetch_data():
    with SgRequests() as session:
        prefectures = []
        for pref in bs(
            session.get(prefecture_url, headers=_headers).text, "lxml"
        ).select("table.wikitable.sortable tbody tr"):
            if pref.th:
                continue
            prefectures.append(pref.select("td")[1].text.strip())

        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        sections = soup.select("section.shop_area_wrap")
        for section in sections:
            _state = section.h2.text.strip()
            if "ONLINE SHOP" in _state:
                break
            locations = section.select("li")
            for _ in locations:
                page_url = _.a["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                _addr = []
                for aa in list(sp1.select_one("div.info_area p").stripped_strings):
                    if "TEL" in aa:
                        break
                    _addr.append(aa)
                raw_address = " ".join(_addr)
                street_address = city = state = ""
                for pref in prefectures:
                    if pref in raw_address:
                        state = pref
                        break
                street_address = _city = raw_address
                if state:
                    street_address = _city = raw_address.replace(state, "")

                if "市" in _city:
                    _city = _city.split("市")
                    if len(_city) > 1:
                        city = _city[0].split()[-1] + "市"
                if city:
                    street_address = street_address.replace(city, "")
                if state == "東京都":
                    city = state
                    state = ""

                pp = sp1.select("div.info_area p")
                hours = ""
                if len(pp) > 1:
                    hours = list(pp[1].stripped_strings)[0]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.h3.text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state or _state,
                    country_code="JP",
                    phone=_.select_one("p.tel_number")
                    .text.replace("TEL", "")
                    .replace(":", "")
                    .strip()
                    if _.select_one("p.tel_number")
                    else "",
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
