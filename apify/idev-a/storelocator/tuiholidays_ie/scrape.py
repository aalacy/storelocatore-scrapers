from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("tui")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tuiholidays.ie"
base_url = "https://www.tuiholidays.ie/shop-finder/directory"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.Directory a ")
        for link in locations:
            page_url = link["href"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers).text
            sp1 = bs(res, "lxml")
            _ = json.loads(sp1.find("script", type="application/ld+json").string)
            addr = _["address"].split(",")
            latitude = res.split("lat:")[1].split(",")[0].strip()
            longitude = res.split("lng:")[1].split("}")[0].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=" ".join(addr[:-2]),
                city=addr[-2].strip(),
                zip_postal=addr[-1].strip(),
                country_code="Ireland",
                phone=_["telephone"],
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_.get("openingHours", [])),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
