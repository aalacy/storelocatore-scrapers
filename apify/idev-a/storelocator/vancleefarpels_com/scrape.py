from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.vancleefarpels.com"
base_url = "https://www.vancleefarpels.com/us/en/store-locator-results-page.stores-with-hours.json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = locator_domain + _["pagePath"]
            street_address = _["address"]["street"]
            if _["address"]["street2"]:
                street_address += " " + _["address"]["street2"]
            hours_of_operation = ""
            raw_hours = _["openingHours"]
            for raw_hour in raw_hours:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + raw_hours[raw_hour][0]["dayOfWeek"]
                    + " "
                    + raw_hours[raw_hour][0]["openingTime"]
                    + "-"
                    + raw_hours[raw_hour][0]["closingTime"]
                ).strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["address"].get("city"),
                state=_["address"].get("state"),
                zip_postal=_["address"].get("zipCode"),
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                country_code=_["address"]["country"],
                phone=_["phoneNumber"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
