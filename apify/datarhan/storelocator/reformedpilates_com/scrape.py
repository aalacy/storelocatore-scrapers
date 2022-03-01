from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://reformedpilates.com/wp-admin/admin-ajax.php?action=store_search&lat=33.496221&lng=-111.964173&max_results=25&search_radius=20&autoload=1"
    domain = "reformedpilates.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        store_url = poi["permalink"]
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["store"]
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = loc_dom.xpath('//p[contains(text(), "PHONE:")]/text()')
        phone = phone[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
