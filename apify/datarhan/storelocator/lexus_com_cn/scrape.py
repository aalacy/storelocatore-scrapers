import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.com.cn/json/dealerdata?variable=1"
    domain = "lexus.com.cn"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = response.text.split("var DEALERS =")[-1]

    all_locations = json.loads(data)
    for poi in all_locations:
        geo = poi["MapCode"].split(",")
        page_url = poi["Url"]
        if not page_url:
            page_url = "https://www.lexus.com.cn/dealer"
        location_type = poi["TypeName"]
        if location_type.endswith(","):
            location_type = location_type[:-1]
        location_type = location_type.replace("0", "全部经销商").replace("1", "认证二手车经销商")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Name"],
            street_address=poi["Address"],
            city=poi["City"],
            state=poi["Province"],
            zip_postal=poi["ZipCode"],
            country_code="CN",
            store_number=poi["ID"],
            phone=poi["Tel"],
            location_type=location_type,
            latitude=geo[0],
            longitude=geo[1],
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
