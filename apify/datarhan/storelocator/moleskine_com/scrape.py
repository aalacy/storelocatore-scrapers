from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import (
    DynamicZipSearch,
    Grain_1_KM,
    SearchableCountries,
)


def fetch_data():
    session = SgRequests()

    start_url = "https://www.moleskine.com/on/demandware.store/Sites-Moleskine_NAM-Site/en_US/Stores-SearchResults"
    domain = "moleskine.com"

    all_coodes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=1,
        granularity=Grain_1_KM(),
    )
    for code in all_coodes:
        frm = {"dwfrm_storelocator_country": "US", "dwfrm_storelocator_query": code}
        data = session.post(start_url.format(code), data=frm)
        if data.status_code != 200:
            continue
        data = data.json()
        if not data.get("stores"):
            continue
        for poi in data["stores"]:
            item = SgRecord(
                locator_domain=domain,
                page_url="https://us.moleskine.com/en/store-locator",
                location_name=poi["name"],
                street_address=", ".join(poi["address"]["lines"]),
                city=poi["address"]["city"],
                state="",
                zip_postal=poi["address"]["zip"],
                country_code="US",
                store_number="",
                phone=poi["phone"],
                location_type=poi["type"],
                latitude=poi["coords"][0],
                longitude=poi["coords"][-1],
                hours_of_operation="",
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
