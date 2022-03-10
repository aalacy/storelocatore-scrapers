from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://restolafleur.com"
base_url = "https://restolafleur.com/en/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var stores_json =")[1]
            .split("gmarkers1")[0]
            .strip()
        )
        for _ in locations:
            info = _["en"]
            phone = info["phone"]
            if info["phone_ext"]:
                phone += " # " + info["phone_ext"]
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=info["name"],
                street_address=info["address"],
                city=_["city_en"],
                zip_postal=info["postal_code"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
