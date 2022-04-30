# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude={}&longitude={}&radius=100&langId=-3&storeId=14351"
    domain = "sunglasshut.com/de"
    hdr = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.GERMANY], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr).json()

        for poi in data["locationDetails"]:
            hoo = []
            for e in poi["hours"]:
                if e["open"]:
                    hoo.append(f'{e["localizedDay"]}: {e["open"]} - {e["close"]}')
                else:
                    hoo.append(f'{e["localizedDay"]}: closed')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.sunglasshut.com/de/sunglasses/store-locations",
                location_name=poi["hostName"],
                street_address=poi["address"],
                city=poi["city"],
                state="",
                zip_postal=poi["zip"],
                country_code=poi["countryCode"],
                store_number=poi["id"],
                phone=poi["shippingDetails"]["phone"],
                location_type=poi["storeType"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
