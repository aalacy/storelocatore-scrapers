from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mostazaweb.com.ar"
base_url = "https://www.mostazaweb.com.ar/locales/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('"places":')[1]
            .split(',"styles":')[0]
        )
        for _ in locations:
            addr = _["location"]
            hours_of_operation = ""
            if _["content"]:
                hours_of_operation = "; ".join(
                    bs(_["content"], "lxml").stripped_strings
                )
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=_["address"],
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr.get("postal_code"),
                latitude=addr["lat"],
                longitude=addr["lng"],
                country_code="AR",
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
