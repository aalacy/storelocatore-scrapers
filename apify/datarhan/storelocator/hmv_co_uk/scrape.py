from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests(verify_ssl=False)
    domain = "hmv.com"
    start_url = (
        "https://store.hmv.com/api/stores?postcode={}&limitTo=30&source=StoreFinder"
    )
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=5
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr).json()
        for poi in data["stores"]:
            street_address = poi["addressOne"]
            if poi["addressTwo"]:
                street_address += " " + poi["addressTwo"]
            street_address = " ".join(street_address.split())
            hoo = etree.HTML(poi["openingTimes"]).xpath("//text()")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://store.hmv.com/store-finder",
                location_name=poi["storeName"],
                street_address=street_address,
                city=poi["city"],
                state="",
                zip_postal=poi["postcode"],
                country_code="",
                store_number=poi["storeId"],
                phone=poi["telephone"],
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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
