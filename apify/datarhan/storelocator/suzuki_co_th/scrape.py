from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzuki.co.th/api/dealer/get"
    domain = "suzuki.co.th"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "_token": "tHHsUP98cU6xSSS1MfQk6lJ0wZI2BuzsjRRbFZsN",
        "province_id": "",
        "district_id": "",
        "sub_district_id": "",
        "zipcode": "",
        "keyword": "",
    }

    data = session.post(start_url, headers=hdr, data=frm).json()
    for poi in data["data"]:
        location_type = poi["service_en"]
        if location_type == "Body & Paint Service":
            continue
        phone = poi["tel"].split(",")[0].strip()
        if phone == "-":
            phone = ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.suzuki.co.th/dealer",
            location_name=poi["name_en"],
            street_address=poi["address_en"],
            city=poi["province_en"],
            state=poi["district_en"],
            zip_postal=poi["postcode_en"],
            country_code="TH",
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi.get("latitute"),
            longitude=poi.get("longitute"),
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
