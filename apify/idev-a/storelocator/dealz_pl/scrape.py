from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dealz.pl"
base_url = "https://www.dealz.pl/sklepy/"


def _coord(locs, nn):
    for ll in locs:
        if str(ll["shop_id"]) == nn:
            return ll


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locs = json.loads(
            soup.select_one("div#js-shops-map")["shops-map-markers"].replace(
                "&quot;", '"'
            )
        )
        locations = soup.select("div.find-shop-box")
        for _ in locations:
            coord = _coord(locs, _["shops-map-marker-anchor"])
            raw_address = " ".join(_.select("div.col-24")[2].stripped_strings)
            addr = raw_address.split(",")
            hours = (
                "; ".join(
                    _.select_one("div.find-shop-box__open-hours").stripped_strings
                )
                .replace("\n", "; ")
                .replace("\r", "")
            )
            yield SgRecord(
                page_url=base_url,
                store_number=_["shops-map-marker-anchor"],
                location_name=_.h3.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=" ".join(addr[-1].split()[1:]),
                zip_postal=addr[-1].strip().split()[0].strip(),
                country_code="Poland",
                latitude=coord["coordinates"]["lat"],
                longitude=coord["coordinates"]["lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
