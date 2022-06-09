from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests("es")
    start_url = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude={}&longitude={}&radius=100&langId=-5&storeId=13251"
    domain = "sunglasshut.com/es"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/plain, */*",
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.SPAIN], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr)
        if data.status_code != 200:
            continue
        data = data.json()
        all_locations = data["locationDetails"]
        for poi in all_locations:
            hoo = []
            for e in poi["hours"]:
                hoo.append(f'{e["day"]} {e["open"]} - {e["close"]}')
            hoo = " ".join(hoo)
            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.sunglasshut.com/es/sunglasses/store-locations",
                location_name=poi["displayAddress"],
                street_address=poi["shippingDetails"]["street"],
                city=poi["shippingDetails"]["city"].split(",")[0],
                state="",
                zip_postal=poi["shippingDetails"]["zipCode"],
                country_code=poi["shippingDetails"]["country"],
                store_number=poi["id"],
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
