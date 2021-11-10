from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.macados.net/wp-admin/admin-ajax.php?action=store_search&lat=37.27032&lng=-79.94327&max_results=25&search_radius=25&autoload=1"
    domain = "macados.net"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()

    for poi in all_locations:
        page_url = "https://www.macados.net/locations/"
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        hoo = []
        if poi["hours"]:
            hoo = etree.HTML(poi["hours"]).xpath("//text()")
        hoo = " ".join(hoo)
        location_type = ""
        if poi["temp_closed"] == "1":
            location_type = "Temporarily closed"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["store"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number="",
            phone=poi["phone"],
            location_type=location_type,
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
