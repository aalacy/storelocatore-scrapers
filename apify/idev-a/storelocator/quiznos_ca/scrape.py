from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.quiznos.ca"
base_url = "https://restaurants.quiznos.ca/api/stores-by-bounds?bounds={%22south%22:-40.61291671623508,%22west%22:-180,%22north%22:83.80643139134396,%22east%22:180}"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_records(http):
    locations = http.get(base_url, headers=_headers).json()
    for _ in locations:
        street_address = _["address_line_1"]
        if _["address_line_2"]:
            street_address += " " + _["address_line_2"]
        hours = []
        for day in days:
            day = day.lower()
            if _.get(f"hour_open_{day}"):
                times = _[f"hour_open_{day}"]
                hours.append(f"{day}: {times}")
        yield SgRecord(
            page_url="https://restaurants.quiznos.ca/en",
            location_name=_["name"],
            store_number=_["number"],
            street_address=street_address,
            city=_["city"],
            state=_["province"],
            zip_postal=_["postal_code"],
            country_code=_["country"],
            phone=_["phone_number"],
            latitude=_["latitude"],
            longitude=_["longitude"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgRequests() as http:
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(http):
                writer.write_row(rec)
