from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mercadona.es/"
base_url = (
    "https://www.mercadona.com/estaticos/cargas/data.js?timestamp=%271637883948973%27"
)


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var dataJson =")[1]
            .strip()[:-1]
        )["tiendasFull"]
        for _ in locations:
            yield SgRecord(
                page_url="https://info.mercadona.es/en/supermercados",
                store_number=_["id"],
                location_name=_["lc"],
                street_address=_["dr"],
                city=_["pv"],
                zip_postal=_["cp"],
                latitude=_["lt"],
                longitude=_["lg"],
                phone=_.get("tf"),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
