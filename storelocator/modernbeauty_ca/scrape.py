from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgscrape.simple_utils import parallelize
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("modernbeauty")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.modernbeauty.com"
base_url = "https://www.modernbeauty.com/locations.html"


def reqs(r, http):
    logger.info(r)
    res = http.get(r, headers=_headers).text
    return res, r


def fetch_data():
    with SgRequests() as http:
        soup = bs(http.get(base_url, headers=_headers).text, "lxml")
        links = [
            locator_domain + link["data-loc"]
            for link in soup.select("div.location_details")
        ]
        logger.info(f"{len(links)} found")
        results = list(
            parallelize(
                search_space=links,
                fetch_results_for_rec=lambda r: reqs(r, http),
                max_threads=4,
            )
        )
        for res, page_url in results:
            state = (
                bs(res, "lxml")
                .select("div.font_size_8")[1]
                .text.split(",")[1]
                .strip()
                .split(" ")[0]
            )
            _ = json.loads(
                res.split("var locations =")[1]
                .split("var ")[0]
                .strip()[:-1]
                .replace("\\n", "##")
                .replace("\\r", "")
                .replace("\\", "")
            )[0]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["loc_value"].replace("NOW OPEN", ""),
                street_address=_["address"].replace("##", ""),
                city=_["city"],
                state=state,
                latitude=_["lat"],
                longitude=_["long"],
                zip_postal=_["postal_code"],
                country_code="CA",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_["store_hours"].split("##")),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
