from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.mcdonalds.com.py/ajax/cobertura.code.php"
    domain = "mcdonalds.com.py"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {"ciudad": "1"}
    data = session.post(start_url, headers=hdr, data=frm).json()

    for poi in data["sucursales"]:
        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.mcdonalds.com.py/cobertura",
            location_name=poi["denominacion"],
            street_address=etree.HTML(poi["info"])
            .xpath('//p[@class="direccion"]/text()')[0]
            .split(":")[-1]
            .strip(),
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=etree.HTML(poi["info"])
            .xpath('//p[@class="tel"]/text()')[0]
            .split(":")[-1]
            .strip(),
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
