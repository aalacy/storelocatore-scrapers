from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.co.kr/json/dealers_index.aspx?v=4"
    domain = "toyota.co.kr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["Exhibition"]:
        page_url = "https://www.toyota.co.kr" + poi[1][0]["website"]
        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi[0]["placeName"],
            street_address=poi[1][0]["address"],
            city="",
            state="",
            zip_postal="",
            country_code="KR",
            store_number="",
            phone=poi[1][0]["tel"],
            location_type="",
            latitude=poi[1][0]["lat"],
            longitude=poi[1][0]["lng"],
            hours_of_operation="",
            raw_address=poi[1][0]["address"],
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
