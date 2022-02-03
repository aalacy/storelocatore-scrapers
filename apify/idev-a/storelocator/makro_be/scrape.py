from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.be"
base_url = "https://www.makro.be/services/StoreLocator/StoreLocator.ashx?id={A8772371-9A6C-481E-A254-F24D266CE069}&lat=50.846704&lng=4.346408&language=nl-BE&distance=10000000&limit=100"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]
        for _ in locations:
            hours = []
            for hh in _["openinghours"].get("all", []):
                hours.append(f"{hh['title']}: {hh['hours']}")
            yield SgRecord(
                page_url=_["link"],
                store_number=_["hnumber"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lon"],
                country_code="Belgium",
                phone=_["telnumber"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
