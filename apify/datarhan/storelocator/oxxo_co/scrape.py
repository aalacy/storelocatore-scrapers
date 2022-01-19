from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.oxxo.co/api/get-tiendas?plaza=&latitude=39.53698983041732&longitude=-0.534440644262757"
    domain = "oxxo.co"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()

    for poi in all_locations:
        city = poi["colonia"]
        if city == "CALLE 52":
            city = SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.oxxo.co/ubicaciones",
            location_name=f'OXXO | {poi["calle"]}',
            street_address=poi["calle"],
            city=city,
            state=SgRecord.MISSING,
            zip_postal=poi["cp"],
            country_code="CO",
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
