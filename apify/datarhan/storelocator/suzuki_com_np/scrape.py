from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://suzuki.com.np/home/getDealers"
    domain = "suzuki.com.np"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {"_token": "ajkdasdajajkdjkhdjasdhaskdhasjkhdjk", "type": "1"}
    data = session.post(start_url, headers=hdr, data=frm).json()

    for store_number, poi in data["dealers"].items():
        if poi["dealer_type"] != 1:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://suzuki.com.np/home/locate_dealer",
            location_name=poi["name"],
            street_address=poi["address_1"],
            city=poi["city_name"],
            state=poi["district_name"],
            zip_postal="",
            country_code="NP",
            store_number=store_number,
            phone=poi["phone_1"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
