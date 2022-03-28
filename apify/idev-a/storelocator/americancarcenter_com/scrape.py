from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("americancarcenter")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.americancarcenter.com"
base_url = "https://www.americancarcenter.com/locations-at-american-car-center"


def _d(sp1, name):
    locs = sp1.find_all(
        "script",
        string=re.compile(
            r"window.inlineJS.push\(function\(\) \{ Moff\.modules\.get\('DataLayer'\)\.pushData\('DealerObject"
        ),
    )
    for loc in locs:
        _ = json.loads('{"id"' + loc.string.split('{"id"')[1].split("});")[0] + "}")
        if _["name"] == name:
            return _


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("main.js-layout-main-block div.container p a")
        for loc in locations:
            page_url = locator_domain + loc["href"].replace(" ", "-")
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            hours = []
            if res.status_code == 200:
                sp1 = bs(res.text, "lxml")
                hours = [
                    " ".join(hh.stripped_strings)
                    for hh in sp1.select("div.widget-paragraph table tr")
                ]
                ss = _d(sp1, sp1.select("div.widget-paragraph p")[1].text.strip())
                yield SgRecord(
                    page_url=page_url,
                    store_number=ss["id"],
                    location_name=ss["name"],
                    street_address=ss["address"],
                    city=ss["city"],
                    state=ss["state"],
                    zip_postal=ss["zip"],
                    country_code="US",
                    phone=ss["phone"] if ss["phone"] else ss["phone2"],
                    latitude=ss["lat"],
                    longitude=ss["lng"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
