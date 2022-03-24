# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://apigw.coles.com.au/digital/colesweb/v1/stores/search?latitude={}&longitude={}&brandIds=2,1&numberOfStores=10"
    domain = "coles.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr).json()
        for poi in data["stores"]:
            hoo = []
            for e in poi["tradingHours"]:
                hoo.append(f'{e["daysOfWeek"]}: {e["storeTime"]}')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.coles.com.au/stores",
                location_name=poi["storeName"],
                street_address=poi["address"],
                city=poi["suburb"],
                state=poi["state"],
                zip_postal=poi["postcode"],
                country_code="AU",
                store_number=poi["storeId"],
                phone=poi["phone"],
                location_type=poi["brandName"],
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
