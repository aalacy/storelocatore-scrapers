# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.truist.com/truist-api/locator/locations.json?returnBranchATMStatus=Y&maxResults=100&locationType=BOTH&searchRadius=40&address={}"
    domain = "truist.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=40
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()
        if not data.get("location"):
            continue
        for poi in data["location"]:
            hoo = " ".join(poi["lobbyHours"]) if poi.get("lobbyHours") else ""

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.truist.com/locations",
                location_name=poi["locationName"],
                street_address=poi["locationAddress"]["address1"],
                city=poi["locationAddress"]["city"],
                state=poi["locationAddress"]["state"],
                zip_postal=poi["locationAddress"]["zipCode"],
                country_code="",
                store_number=poi.get("branchId"),
                phone=poi["phone"],
                location_type=poi["locationType"],
                latitude=poi["locationAddress"]["lat"],
                longitude=poi["locationAddress"]["long"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
