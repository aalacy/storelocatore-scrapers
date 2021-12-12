from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.hibdontire.com/bsro/services/store/location/get-list-by-zip?zipCode={}"
    domain = "hibdontire.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()
        if not data["data"].get("stores"):
            continue
        for poi in data["data"]["stores"]:
            hoo = []
            for e in poi["hours"]:
                hoo.append(f'{e["weekDay"]}: {e["openTime"]} - {e["closeTime"]}')
            hoo = " ".join(hoo)
            if "SUN:" not in hoo:
                hoo += " " + "SUN: closed"

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["localPageURL"],
                location_name=poi["storeName"],
                street_address=poi["address"],
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["zip"],
                country_code="",
                store_number=poi["storeNumber"],
                phone=poi["phone"],
                location_type=poi["storeType"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
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
