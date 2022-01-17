from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.wingstop.com.sg"
base_url = "https://api.wingstop.com.sg/restaurants/?nomnom=calendars"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            temp = {}
            hours = []
            for hr in _["calendars"]:
                if hr["label"] == "Delivery":
                    for hh in hr["ranges"]:
                        temp[
                            hh["weekday"]
                        ] = f"{hh['start'].split()[-1]} - {hh['end'].split()[-1]}"
            for day in days:
                hours.append(f"{day}: {temp[day]}")
            yield SgRecord(
                page_url=_["nomnom"]["redirect"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["streetaddress"],
                city=_["city"],
                state=_.get("state"),
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="SG",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
