from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.zoundshearing.com/corp/wp-admin/admin-ajax.php"
    domain = "zoundshearing.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "address": "",
        "formdata": "addressInput=",
        "lat": "33.4483771",
        "lng": "-112.0740373",
        "name": "",
        "radius": "5000",
        "tags": "",
        "action": "csl_ajax_onload",
    }
    data = session.post(start_url, headers=hdr, data=frm).json()

    all_locations = data["response"]
    for poi in all_locations:
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        hoo = poi["hours"].strip().replace("&amp;", "&").replace("&lt;br&gt;", "")
        if hoo == "Call for Appointment":
            hoo = ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.zoundshearing.com/corp/storelocator/",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number="",
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
