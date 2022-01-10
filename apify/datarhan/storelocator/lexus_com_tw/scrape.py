import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.com.tw/location.aspx#"
    domain = "lexus.com.tw"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
    }
    frm = {"ORGKINDID": "02"}
    data = session.post(
        "https://www.lexus.com.tw/WS_Owners.asmx//GetLocation", json=frm, headers=hdr
    ).json()
    all_locations = json.loads(data["d"])

    for poi in all_locations["DATA"]:
        hoo = f"WEEKDAYTIME {poi['WEEKDAYTIME']}, WEEKENDTIME {poi['WEEKENDTIME']}"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["BRANCHFULLNM"],
            street_address=poi["ADDR"],
            city=poi["COMPNM"],
            state=poi["DISTIRCT"],
            zip_postal=poi["ZIP"],
            country_code="TW",
            store_number=poi["BRANCHID"],
            phone=poi["TEL"],
            location_type="",
            latitude=poi["LATITUDE"],
            longitude=poi["LONGITUDE"],
            hours_of_operation=hoo,
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
