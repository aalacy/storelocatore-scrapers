from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.myplacehotels.com/"
base_url = "https://www.myplacehotels.com/search"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(
            soup.find("script", string=re.compile(r"propertiesList"))
            .string.split("propertiesList =")[1]
            .strip()[:-1]
        )
        for key, _ in locations.items():
            page_url = locator_domain + _["slug"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["street_address"],
                city=_["city_name"],
                state=_["state_name"],
                zip_postal=_["zip"],
                country_code=_["country_name"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
