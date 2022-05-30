from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thekooples.com"
base_url = "https://www.thekooples.com/uk_en/retailer/retailer"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("window.retailerLocatorData   =")[1]
            .split("window")[0]
            .strip()[:-1]
        )["retailers"]
        for _ in locations:
            page_url = f"https://www.thekooples.com/uk_en/retailer/presentation/retailer/urlKey/{_['url_key']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["retailer_id"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                zip_postal=_["zip_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone_number"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
