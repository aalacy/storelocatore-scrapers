from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("family")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://family.co.jp/"
base_url = "https://as.chizumaru.com/famimatg/top?account=famimatg&accmd=0"
pref_url = "https://as.chizumaru.com/famimatg/articleList?account=famimatg&accmd=0&searchType=True&adr={}&c2=1&pg={}&pageSize=500&pageLimit=10000&template=Ctrl%2fDispListArticle_g12"
prefecture_url = "https://en.wikipedia.org/wiki/Prefectures_of_Japan"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        prefectures = []
        for pref in bs(
            session.get(prefecture_url, headers=_headers).text, "lxml"
        ).select("table.wikitable.sortable tbody tr"):
            if pref.th:
                continue
            prefectures.append(pref.select("td")[1].text.strip())

        sp1 = bs(session.get(base_url, headers=_headers).text, "lxml")
        prefs = sp1.select("select.cz_select01 option")
        for pref in prefs:
            if not pref.get("value"):
                continue
            page = 1
            while True:
                sp2 = bs(
                    session.get(
                        pref_url.format(pref["value"], page), headers=_headers
                    ).text,
                    "lxml",
                )
                locations = sp2.select("div.cz_articlelist_box")
                if not locations:
                    break
                logger.info(f"{pref['value']} [page {page}] {len(locations)}")
                page += 1
                for _ in locations:
                    tr = _.select("dd table tbody tr")
                    page_url = "https://as.chizumaru.com" + tr[0].a["href"]
                    raw_address = tr[1].td.text.strip()
                    street_address = city = state = ""
                    for _pref in prefectures:
                        if _pref in raw_address:
                            state = _pref
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

                    phone = ""
                    if _.find("a", href=re.compile(r"tel:")):
                        phone = _.find("a", href=re.compile(r"tel:")).text.strip()

                    yield SgRecord(
                        page_url=page_url,
                        location_name=tr[0].td.text.strip(),
                        street_address=street_address,
                        city=city,
                        state=state,
                        country_code="JP",
                        phone=phone,
                        locator_domain=locator_domain,
                        hours_of_operation=tr[3].td.text.strip(),
                        raw_address=raw_address,
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
