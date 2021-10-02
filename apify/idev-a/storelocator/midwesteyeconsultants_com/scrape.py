from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("midwesteyeconsultants")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.midwesteyeconsultants.com"
base_url = "https://www.midwesteyeconsultants.com/locations/"


def _ll(locs, id):
    _loc = {}
    for loc in locs:
        if str(loc["id"]) == id:
            _loc = loc
            break

    return _loc


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        soup = bs(res, "lxml")
        locs = json.loads(
            res.split("var oms_locations =")[1]
            .split("var oms_snazzy_m")[0]
            .strip()[:-1]
        )
        locations = soup.select('div#locations_list script[type="html/template"]')
        for _ in locations:
            id = _["id"].split("_")[-1]
            page_url = bs(_.string, "lxml").a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one("div.list--row--address").stripped_strings)[1:]
            phone = ""
            if sp1.select_one("a.location_phone_number"):
                phone = sp1.select_one("a.location_phone_number").text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=id,
                location_name=bs(_.string, "lxml").a.text.split("–")[-1].strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=_ll(locs, id)["lat"],
                longitude=_ll(locs, id)["lng"],
                hours_of_operation="; ".join(
                    sp1.select_one("div.list--row--hours p").stripped_strings
                ),
                locator_domain=locator_domain,
                raw_address=" ".join(addr[:2]),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
