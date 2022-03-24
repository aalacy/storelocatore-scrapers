# -*- coding: utf-8 -*-

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://www.repsol.com/App/SA/CanalMovilREST/api/v1/EESS/list_lite.json"
    )
    domain = "repsol.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.repsol.com/app/sa/herramientas/buscadorestacionesservicio/",
            location_name=poi["Nombre"],
            street_address=poi["Direccion"],
            city=poi["Localidad"],
            state=poi["Provincia"],
            zip_postal=poi["CodigoPostal"],
            country_code="",
            store_number=poi["Id"],
            phone="",
            location_type="",
            latitude=poi["X"],
            longitude=poi["Y"],
            hours_of_operation="",
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
