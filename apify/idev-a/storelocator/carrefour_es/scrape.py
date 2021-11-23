from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.es"
base_url = "https://www.carrefour.es/tiendas-carrefour/buscador-de-tiendas/locations.aspx?origLat=40.4167754&origLng=-3.7037902"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "marker"
        )
        for _ in locations:
            street_address = _["address"]
            if _.get("address2"):
                street_address += " " + _["address2"]
            hours = ""
            if _["hours1"]:
                if "apertura" not in _["hours1"].lower():
                    hours = f"L - S: {_['hours1']}"
            page_url = locator_domain + _["web"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Spain",
                phone=_["phone"],
                location_type=_["category"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
