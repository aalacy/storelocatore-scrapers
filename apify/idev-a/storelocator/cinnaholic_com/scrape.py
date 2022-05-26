from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("cinnaholic")

_header1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}
locator_domain = "https://cinnaholic.com"
base_url = "https://locations.cinnaholic.com/modules/multilocation/?near_lat=37.09024&near_lon=-95.712891&threshold=4000&geocoder_region=&distance_unit=miles&limit=200&services__in=&language_code=en-us&published=1&within_business=true"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_header1).json()["objects"]
        for _ in locations:
            street_address = _["street"]
            if _["street2"]:
                street_address += " " + _["street2"]
            hours = []
            for hh in _.get("formatted_hours", {}).get("primary", {}).get("days", []):
                hours.append(f"{hh['label']}: {hh['content']}")
            yield SgRecord(
                page_url=_["location_url"],
                store_number=_["id"],
                location_name=_["location_name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["lat"],
                longitude=_["lon"],
                country_code=_["country"],
                phone=_["phonemap"]["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["formatted_address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
