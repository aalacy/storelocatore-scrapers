# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.exxon.com/en/api/locator/Locations?Latitude1={}&Latitude2={}&Longitude1={}&Longitude2={}&DataSource=RetailGasStations&Country=US&Customsort=False"
    domain = "exxon.com"

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=10
    )
    for lat, lng in all_coords:
        url = start_url.format(lat, lat + 0.4, lng, lng + 1.0)
        try:
            all_locations = session.get(url).json()
        except Exception:
            continue
        for poi in all_locations:
            street_address = poi["AddressLine1"]
            if poi["AddressLine2"]:
                street_address += ", " + poi["AddressLine2"]
            hoo = ""
            if poi["WeeklyOperatingHours"]:
                hoo = etree.HTML(poi["WeeklyOperatingHours"]).xpath("//text()")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.exxon.com/en/find-station/",
                location_name=poi["LocationName"],
                street_address=street_address,
                city=poi["City"],
                state=poi["StateProvince"],
                zip_postal=poi["PostalCode"],
                country_code=poi["Country"],
                store_number=poi["LocationID"],
                phone=poi["Telephone"],
                location_type=poi["EntityType"],
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
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
