from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.schewelshome.com/"
base_url = "https://www.schewelshome.com/stores/"


def _hp(locs, name):
    for loc in locs:
        if loc.select_one("div.flv4-store-name").text.strip() == name:
            phone = ""
            if loc.select_one("div.flv4-store-phone1"):
                phone = loc.select_one("div.flv4-store-phone1").text.strip()
            elif loc.select_one("div.flv4-store-phone2"):
                phone = loc.select_one("div.flv4-store-phone2").text.strip()
            hours = list(loc.select_one("div.flv4-store-hours").stripped_strings)
            return phone, hours, loc["href"]


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("var mapData =")[1].split("if (mapData")[0].strip()[:-1]
        )[0]["Markers"]
        locs = bs(res, "lxml").select("a.flv4-store")
        for _ in locations:
            info = bs(_["storeAddress"], "lxml")
            addr = list(info.stripped_strings)
            phone, hours, page_url = _hp(locs, _["storeName"])
            yield SgRecord(
                page_url=page_url,
                location_name=_["storeName"],
                street_address=info.select_one('span[itemprop="streetAddress"]')
                .text.replace("Shoppes Of Appomattox", "")
                .strip(),
                city=info.select_one('span[itemprop="addressLocality"]').text.strip(),
                state=info.select_one('span[itemprop="addressRegion"]').text.strip(),
                zip_postal=addr[-1],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
