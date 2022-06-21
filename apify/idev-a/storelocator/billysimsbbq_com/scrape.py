from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "https://billysimsbbq.com"
base_url = "https://taptapeat.com/locations/?bid=108&lat=37.09024&lng=-95.712891"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        locations = driver.execute_script("return restaurants")
        for id, _ in locations.items():
            street_address = _["vcAddress"]
            if _.get("vcAddress2"):
                street_address += " " + _.get("vcAddress2")
            hours = []
            if _["hours"]:
                for x, hh in _["hours"].items():
                    if hh:
                        hours.append(
                            f"{hh[0]['DayOfWeek_Day']}: {hh[0]['vcTimeOpen']} - {hh[0]['vcTimeClose']}"
                        )
            yield SgRecord(
                page_url="https://billysimsbbq.com/locations/",
                store_number=id,
                location_name=_["vcFriendlyName"],
                street_address=street_address,
                city=_["vcCity"],
                state=_["vcState"],
                zip_postal=_["vcZip"],
                latitude=_["vcLatitude"],
                longitude=_["vcLongitude"],
                country_code="US",
                phone=_.get("vcPhoneNumber"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
