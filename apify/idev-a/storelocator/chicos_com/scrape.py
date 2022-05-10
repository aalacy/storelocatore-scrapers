from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.chicos.com"
base_url = "https://www.chicos.com/locations/modules/multilocation/?near_location=10001&services__in=&language_code=en-us&published=1&within_business=true&limit=1000"


def fetch_data():
    with SgRequests() as session:
        data = session.get(base_url, headers=_headers).json()
        for _ in data["objects"]:
            hours = []
            for hh in (
                _.get("formatted_hours", {}).get("primary", {}).get("grouped_days", [])
            ):
                hours.append(f"{hh['label']}: {hh['content']}")
            yield SgRecord(
                page_url=_["location_url"],
                store_number=_["id"],
                location_name=_["city"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["lat"],
                longitude=_["lon"],
                country_code=_["country"],
                phone=_["phonemap"].get("phone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["formatted_address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
