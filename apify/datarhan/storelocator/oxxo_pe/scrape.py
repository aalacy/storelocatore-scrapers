from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.oxxo.pe/api/get-tiendas?plaza=&latitude=39.53698983041732&longitude=-0.534440644262757"
    domain = "oxxo.pe"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }
    all_locations = session.get(start_url, headers=hdr).json()

    for poi in all_locations:
        stree_address = poi["calle"]
        if poi["numero"]:
            stree_address += " " + poi["numero"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.oxxo.pe/ubicaciones",
            location_name=f'OXXO | {poi["calle"]}',
            street_address=stree_address,
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code="PE",
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
