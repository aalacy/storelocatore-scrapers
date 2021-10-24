from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("kiplingmexico")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kiplingmexico.com"
base_url = "https://kiplingmexico.com/apps/store-locator/"


def fetch_data():
    with SgRequests() as session:
        locations = (
            session.get(base_url, headers=_headers)
            .text.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&#039;", '"')
            .split("markersCoords.push(")[1:-2]
        )
        for loc in locations:
            _ = json.loads(loc.split(");")[0].strip())
            if not _["address"]:
                continue
            info = bs(_["address"], "lxml")
            street_address = info.select_one(".address").text.strip()
            addr2 = info.select_one(".address2")
            if addr2 and addr2.text.strip():
                street_address += " " + addr2.text.strip()
            zip_postal = state = ""
            if info.select_one(".postal_zip"):
                zip_postal = info.select_one(".postal_zip").text.strip()

            if info.select_one(".prov_state"):
                state = info.select_one(".prov_state").text.strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=info.select_one(".name").text.strip(),
                street_address=street_address,
                city=info.select_one(".city").text.strip(),
                state=state,
                zip_postal=zip_postal,
                country_code="Mexico",
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
