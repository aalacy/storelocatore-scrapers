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

locator_domain = "https://www.mightyquinnsbbq.com"
base_url = "https://www.mightyquinnsbbq.com/mighty-quinns-locator/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("locations:")[1]
            .split("apiKey:")[0]
            .strip()[:-1]
        )
        for _ in locations:
            page_url = locator_domain + _["url"]
            country_code = "US"
            if "Dubai" in _["name"]:
                country_code = "UAE"
            hours = list(bs(_["hours"], "lxml").stripped_strings)
            if hours and "Soon" in hours[0]:
                continue
            if hours and "open" in hours[0]:
                hours = []
            state = _["state"]
            if state == "United Arab Emirates":
                state = ""
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=state,
                zip_postal=_["postal_code"],
                country_code=country_code,
                phone=_["phone_number"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\xa0", ""),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
