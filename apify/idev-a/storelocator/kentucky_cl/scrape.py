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

locator_domain = "https://www.kentucky.cl"
base_url = "https://www.kentucky.cl/nuestras-tiendas"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml").select_one(
                'div[data-controller="maps"]'
            )["data-maps-collection-value"]
        )
        for key, locs in locations.items():
            if not key:
                continue
            for _ in locs:
                phone = _["phone"]
                if phone == "000000000":
                    phone = ""
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=_["address1"],
                    city=_["city"],
                    state=_["state_name"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="Chile",
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
