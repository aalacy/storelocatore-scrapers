from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import dirtyjson as json

logger = SgLogSetup().get_logger("bairstoweves")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.bairstoweves.co.uk"
base_url = "https://www.bairstoweves.co.uk/api/branch/?brands=11&brands=12&page={}&pageSize=100&pageUrl=%2Fbranch%2F&placeId=0&searchUrl=%2Fbranches%2F"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            locations = session.get(base_url.format(page), headers=_headers).json()[
                "cards"
            ]
            if not locations:
                break
            page += 1
            logger.info(f"page {page} {len(locations)}")
            for _ in locations:
                page_url = _["detailsUrl"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("table.table--opening-times tr")
                ]
                coord = json.loads(sp1.select_one("div.details-panel")["data-location"])
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=_["streetAddress"],
                    city=_["locality"].split(",")[-1],
                    state=_["region"],
                    zip_postal=_["postcode"],
                    latitude=coord["lat"],
                    longitude=coord["lng"],
                    country_code="UK",
                    phone=_["telephoneNumber"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
