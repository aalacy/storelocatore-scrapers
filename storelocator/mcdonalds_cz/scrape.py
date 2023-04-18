from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = ""
base_url = "https://restaurace.mcdonalds.cz/api?token=7983978c4175e5a88b9a58e5b5c6d105217fbc625b6c20e9a8eef3b8acc6204f"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["restaurants"]
        for _ in locations:
            if _["status"] == "invisible":
                continue
            hours = []
            for x, hh in enumerate(_["worktime"]):
                if hh:
                    hours.append(f"{days[x]}: {hh}")
            if _["status"] != "open":
                hours = []
            page_url = f"https://restaurace.mcdonalds.cz/{_['slug']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Czech Republic",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
