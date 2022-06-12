import re
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.visitcompletecare.com/wp-json/wp/v2/pages?per_page=70&parent=2927,10,"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        if not poi["acf"].get("location_info"):
            continue
        store_url = poi["link"]
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["acf"]["location_info"]["nickname"]
        if not location_name:
            continue
        location_name = location_name.replace("<br/>", "")
        street_address = poi["acf"]["location_info"]["address_1"]
        addr = parse_address_intl(poi["acf"]["location_info"]["address_2"])
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["acf"]["location_info"]["phone_number"]
        location_type = "<MISSING>"
        latitude = poi["acf"]["location_info"]["latitude"]
        longitude = poi["acf"]["location_info"]["longitude"]
        hoo = loc_dom.xpath('//p[contains(text(), "Open 24/7")]/text()')[0]
        hoo = hoo.split(". No")[0]

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
