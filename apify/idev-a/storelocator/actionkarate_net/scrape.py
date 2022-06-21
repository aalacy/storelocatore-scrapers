from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://actionkarate.net/"
base_url = "https://actionkarate.net/locations/"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        driver.wait_for_request("state.js")
        script = "return __NUXT__.state.locations"
        locations = driver.execute_script(script)
        for _ in locations:
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["city"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"]["name"],
                zip_postal=_["zip_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
