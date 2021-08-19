from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kfc.co.nz/find-a-kfc"
urls = [
    "https://api.kfc.co.nz/find-a-kfc/rckq",
    "https://api.kfc.co.nz/find-a-kfc/rckn",
]

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def fetch_data():
    with SgRequests() as session:
        for base_url in urls:
            locations = session.get(base_url, headers=_headers).json()["Value"]
            for _ in locations:
                page_url = f"https://kfc.co.nz/find-a-kfc/{_['url']}"
                hours = []
                for hh in _["operatingHoursStore"]:
                    hours.append(f"{days[hh['dayOfWeek']]}: {hh['start']}-{hh['end']}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=_["address"]
                    .replace(_["city"], "")
                    .replace("New Zealand", "")
                    .replace(",", ""),
                    city=_["city"],
                    zip_postal=_["postalcode"],
                    latitude=_["location"]["latitude"],
                    longitude=_["location"]["longitude"],
                    country_code="New Zealand",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
