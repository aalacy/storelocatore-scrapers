from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://global.diesel.com/"
base_url = "https://global.diesel.com/on/demandware.store/Sites-DieselNonEcommerce-Site/en_TR/StoreFinder-SearchByBoundaries?latmin=-180&latmax=180&lngmin=-180&lngmax=180"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]["stores"]
        for _ in locations:
            hours = []
            for hh in _.get("working_days", []):
                times = "closed"
                if hh["hours"]:
                    times = ",".join(hh["hours"])
                hours.append(f"{hh['day']}: {times}")
            page_url = f"https://global.diesel.com/store-detail?sid={_['ID']}"
            location_type = ""
            if _.get("isOpen", {}).get("status", "").lower() == "closed":
                location_type = "closed"
            yield SgRecord(
                page_url=page_url,
                store_number=_["ID"],
                location_name=_["name"],
                street_address=_["schema"]["address"]["streetAddress"],
                city=_["city"],
                state=_.get("stateCode"),
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["countryCode"],
                phone=_.get("phone"),
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
