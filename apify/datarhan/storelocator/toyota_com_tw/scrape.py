from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.com.tw/api/location.ashx"
    domain = "toyota.com.tw"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {"TYPE": "1"}
    data = session.post(start_url, data=frm, headers=hdr).json()

    for poi in data["DATA"]:
        location_name = f'{poi["DEALER"]} {poi["TITLE"]}'
        if poi["TYPE"] != "1":
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.toyota.com.tw/location.aspx",
            location_name=location_name,
            street_address=poi["ADDR"],
            city=poi["CITY"],
            state=poi["AREA"],
            zip_postal="",
            country_code="TW",
            store_number=poi["KEY"],
            phone=poi["TEL"],
            location_type="",
            latitude=poi["LAT"],
            longitude=poi["LNG"],
            hours_of_operation=poi["TIME"],
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
