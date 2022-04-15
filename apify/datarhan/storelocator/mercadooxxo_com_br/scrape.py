from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.mercadooxxo.com.br/api/get-tiendas?estado=&latitude={}&longitude={}"
    domain = "mercadooxxo.com.br"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRAZIL], expected_search_radius_miles=500
    )
    all_locations = []
    for lat, lng in all_coords:
        all_locations += session.get(start_url.format(lat, lng), headers=hdr).json()

    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.mercadooxxo.com.br/lojas",
            location_name=f'OXXO | {poi["plaza"]}',
            street_address=poi["calle"],
            city=poi["ciudad"],
            state=SgRecord.MISSING,
            zip_postal=poi["cp"],
            country_code="BR",
            store_number=poi["id"],
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=poi["latitud"],
            longitude=poi["longitud"],
            hours_of_operation=SgRecord.MISSING,
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
