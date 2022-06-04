import json
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://sperohealth.com/wp-admin/admin-ajax.php?action=get_locations&security={}"
    domain = "sperohealth.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get("https://sperohealth.com/locations-near-you/")
    dom = etree.HTML(response.text)
    token = dom.xpath('//input[@id="search-location-ajax-nonce"]/@value')[0]

    response = session.get(start_url.format(token), headers=hdr)
    all_locations = json.loads(response.text)

    for poi in all_locations:
        location_name = poi["title"]
        page_url = f'https://sperohealth.com/locations/{location_name.replace(", ", "-").lower()}/'
        addr = parse_address_intl(poi["address"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        store_number = poi["id"]
        phone = poi["phone"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        location_type = ""
        if "Coming Soon" in location_name:
            location_name = location_name.split("(C")[0].strip()
            location_type = "Coming Soon"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
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
