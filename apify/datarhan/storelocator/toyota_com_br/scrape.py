from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.com.br/wp-admin/admin-ajax.php"
    domain = "toyota.com.br"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {"action": "tyt_ajax_get_dealership_by_address", "address": "", "filter": ""}
    data = session.post(start_url, headers=hdr, data=frm).json()

    for poi in data["dealers"]:
        if poi["meta"]["tyt_dealership_type"] != "3S":
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.toyota.com.br/concessionarias/",
            location_name=poi["meta"]["tyt_dealership_trade_name"],
            street_address=poi["meta"]["tyt_dealership_address"],
            city=poi["meta"]["tyt_dealership_city"],
            state=poi["meta"]["tyt_dealership_state"],
            zip_postal=poi["meta"]["tyt_dealership_zip_code"],
            country_code="BR",
            store_number=poi["meta"]["tyt_dealership_toyos"],
            phone=poi["meta"]["tyt_dealership_phone"],
            location_type="",
            latitude=poi["meta"]["tyt_dealership_map"]["lat"],
            longitude=poi["meta"]["tyt_dealership_map"]["lng"],
            hours_of_operation="",
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
