from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

logger = SgLogSetup().get_logger("esso_ca")


def fetch_data():
    session = SgRequests()
    start_url = "https://www.esso.ca/en-CA/api/locator/Locations?Latitude1={}&Latitude2={}&Longitude1={}&Longitude2={}&DataSource=RetailGasStations&Country=CA"
    domain = "esso.ca"
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=25
    )
    for lat, lng in all_coords:
        all_locations = session.get(start_url.format(lat, lat + 1, lng, lng + 1)).json()
        for poi in all_locations:
            city = poi["City"]
            store_number = poi["LocationID"]
            page_url = f"https://www.esso.ca/en-ca/find-station/esso-{city.replace(' ', '-').lower()}-on-esso-{store_number}"
            street_address = poi["AddressLine1"]
            if poi["AddressLine2"]:
                street_address += " " + poi["AddressLine2"]
            hoo = poi["WeeklyOperatingHours"]
            if hoo:
                hoo = etree.HTML(hoo).xpath("//text()")
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["DisplayName"],
                street_address=street_address,
                city=city,
                state=poi["StateProvince"],
                zip_postal=poi["PostalCode"],
                country_code=poi["Country"],
                store_number=store_number,
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
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
