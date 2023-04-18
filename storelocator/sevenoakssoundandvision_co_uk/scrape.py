from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sevenoakssoundandvision.co.uk/"
base_url = "https://www.sevenoakssoundandvision.co.uk/storeinfo.aspx?findstore=1"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("table.stores-table tr")
        for _ in locations:
            page_url = locator_domain + _.select_one("td.store-link a")["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            addr = list(sp1.select_one("div.address").stripped_strings)
            phone = ""
            if _.select_one("a.store-number"):
                phone = _.select_one("a.store-number").text
            info = json.loads(res.split("new GMaps(")[1].split(");")[0])
            hours = []
            for hh in sp1.select("div.open-hours"):
                if "holiday" in hh["class"]:
                    continue
                hours.append(": ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("span.store-name").text.strip(),
                street_address=addr[0],
                city=addr[1].strip(),
                zip_postal=addr[2].strip(),
                country_code="UK",
                phone=phone,
                latitude=info["lat"],
                longitude=info["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr[:2]),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
