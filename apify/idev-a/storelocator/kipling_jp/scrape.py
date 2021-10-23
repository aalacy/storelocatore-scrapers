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

locator_domain = "https://www.kipling.jp"
base_url = "https://www.kipling.jp/stores/info/list"
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
        locations = soup.select("li.store-list")
        for _ in locations:
            raw_address = _.select_one("p.address").text.strip()
            street_address = city = state = ""
            for pref in prefectures:
                if pref in raw_address:
                    state = pref
                    break
            if state:
                _city = raw_address.replace(state, "")
            _city = _city.split("市")
            if len(_city) > 1:
                city = _city[0] + "市"
            street_address = _city[-1]
            if state == "東京都":
                city = state
                state = ""
            _hr = _.select_one("p.hours")
            hours = ""
            if _hr:
                hours = _hr.text.strip()
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
                country_code="JP",
                latitude=coord[1],
                longitude=coord[0],
                phone=_.select_one("p.telephone").text.strip().split(":")[-1],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
