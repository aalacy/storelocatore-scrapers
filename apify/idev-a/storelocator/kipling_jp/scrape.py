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
base_url = "https://www.kipling.jp/stores/info/list?outlet=&shop=&retail=&radius=50&current_lat=&current_lng=&use_my_location=&search=&p=&store-type={}"
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

        for location_type in ["retail", "outlet"]:
            soup = bs(
                session.get(base_url.format(location_type), headers=_headers).text,
                "lxml",
            )
            locations = soup.select("li.store-list")
            logger.info(f"{base_url.format(location_type)} {len(locations)} found")
            for _ in locations:
                raw_address = _.select_one("p.address").text.strip()
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
                        city = _city[0] + "市"
                if city:
                    street_address = street_address.replace(city, "")
                if state == "東京都":
                    city = state
                    state = ""
                _hr = _.select_one("p.hours")
                hours = ""
                if _hr:
                    hours = _hr.text.strip()
                coord = (
                    _.select_one("a.map-open")["href"]
                    .split("||")[-1]
                    .strip()
                    .split(",")
                )
                location_name = "Kipling"
                if location_type == "outlet":
                    location_name = "Kipling Outlet"
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    country_code="JP",
                    latitude=coord[1],
                    longitude=coord[0],
                    location_type=location_type,
                    phone=_.select_one("p.telephone").text.strip().split(":")[-1],
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
