from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.mcdonalds.com.sg/wp/wp-admin/admin-ajax.php?action=store_locator_locations"
    domain = "mcdonalds.com.sg"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = "[]"
    all_locations = session.post(start_url, data=frm, headers=hdr).json()

    for poi in all_locations:
        hoo = ""
        if poi["op_hours"]:
            hoo = etree.HTML(poi["op_hours"]).xpath("//text()")
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            hoo = hoo.split("Main Store: ")[-1].split(" Dessert")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.mcdonalds.com.sg/locate-us/",
            location_name=poi["name"],
            street_address=poi["address"]
            .replace("\r\n", " ")
            .replace("&amp;", "")
            .strip()
            .split("<sup")[0],
            city=poi["city"],
            state=poi["region"],
            zip_postal=poi["zip"],
            country_code="SG",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["long"],
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
