from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ampol.au/"
base_url = "https://www.ampol.com.au/custom/api/locator/get"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["value"]
        for _ in locations:
            hours = []
            if _["OpenAllHours"]:
                hours = ["Open 24 hours"]
            else:
                for day in days:
                    start = f"{day}_Openning"
                    end = f"{day}_Closing"
                    if _[start] == "Midnight" and _[end] == "Midnight":
                        hours = ["Open 24 hours"]
                        break

                    hours.append(f"{day}: {_[start]} - {_[end]}")
            phone = _["Phone"]
            if phone == "0":
                phone = ""
            yield SgRecord(
                store_number=_["LocationID"],
                location_name=_["LocationName"],
                street_address=_["Address"],
                city=_["Suburb"],
                state=_["State"],
                zip_postal=_["Postcode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="Australia",
                phone=phone,
                locator_domain=locator_domain,
                location_type=_["StoreType"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
