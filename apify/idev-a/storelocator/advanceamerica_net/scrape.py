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

locator_domain = "https://www.advanceamerica.net"
base_url = "https://www.advanceamerica.net/store-locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("script", string=re.compile(r"document.addEventListener"))
            .string.split("}',")[-1]
            .split(");")[0]
            .strip()[1:-1]
        )
        for _ in locations:
            page_url = f"https://www.advanceamerica.net/store-locations/california/{_['address'].strip().replace('.','').replace(' ','-')}-{_['city']}-{_['zip']}"
            hours = []
            for hh in _.get("hours", {}).get("items", []):
                times = f"{hh['open_time']}-{hh['close_time']}"
                if not hh["open_time"]:
                    times = "closed"
                hours.append(f"{hh['day']}: {times}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["title"].split("#")[-1],
                location_name=_["title"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
