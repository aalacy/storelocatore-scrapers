from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]

locator_domain = "https://www.kfc.de"
base_url = "https://api.kfc.de/job/storeJobs"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["storeJobs"]
        for _ in locations:
            hours = []
            for hh in _["operatingHours"].get("dinein", []):
                hours.append(f"{days[hh['dayofweek']]}: {hh['start']}-{hh['end']}")
            page_url = f"https://www.kfc.de/find-a-kfc/{_['urlname']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["displayName"],
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["postalcode"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                country_code="Germany",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
