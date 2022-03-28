import re
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://bkchina.cn/restaurant/getMapsListAjax?page=1"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["data"]["data"]
    for p in range(2, int(data["data"]["total"]) // 5 + 2):
        data = session.get(add_or_replace_parameter(start_url, "page", str(p))).json()
        all_locations += data["data"]["data"]

    for poi in all_locations:
        latitude = poi["storeLatitude"]
        longitude = poi["storeLongitude"]
        if float(latitude) > 90.0:
            latitude = poi["storeLongitude"]
            longitude = poi["storeLatitude"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://bkchina.cn/restaurant/index.html",
            location_name=poi["storeName"],
            street_address=poi["storeAddress"].replace("&nbsp;", " "),
            city=poi["storeCity"],
            state=poi["storeProvince"],
            zip_postal=poi["storeZip"],
            country_code=SgRecord.MISSING,
            store_number=poi["storeNo"],
            phone=poi["storePhone"],
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=poi["storeBusinessHours"],
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
