from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("eatphillysbest")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _d(name, locs):
    for _ in locs:
        if _.select_one("span.location_title").text.strip() == name:
            return _
    return None


def fetch_data():
    locator_domain = "https://eatphillysbest.com"
    base_url = "https://eatphillysbest.com/store-locations/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locs = bs(res, "lxml").select("div#all_locations li")
        locations = (
            res.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&#039;", '"')
            .replace("&quot;", '"')
            .split("address_objects.push(")[1:]
        )
        for loc in locations:
            _ = json.loads(loc.split(");")[0])
            addr = parse_address_intl(_["Address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            ll = _d(_["Title"].replace("Philly's Best", "").strip(), locs)
            page_url = locator_domain + ll.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = list(sp1.select_one("div#location_address").stripped_strings)[-2]
            if not hours.startswith("Mon"):
                hours = ""
            store_number = page_url.split("/")[-2]
            phone = list(ll.stripped_strings)[-1]
            yield SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=_["Title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                latitude=_["LatLng"][0],
                longitude=_["LatLng"][1],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=_["Address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
