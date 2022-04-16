from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotaperu.com.pe/traer/puntos/general"
    domain = "toyotaperu.com.pe"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["marcadores"]:
        item = SgRecord(
            locator_domain=domain,
            page_url=poi.get("web"),
            location_name=poi["nombre"],
            street_address=poi["direccion"],
            city=poi["ciudad"],
            state=poi.get("dpto"),
            zip_postal="",
            country_code="PE",
            store_number="",
            phone=poi["telefono"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["long"],
            hours_of_operation=poi["horario"],
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
