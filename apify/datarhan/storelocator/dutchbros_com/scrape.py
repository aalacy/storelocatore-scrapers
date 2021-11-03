import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "dutchbros.com"
    start_url = "https://files.dutchbros.com/api-cache/stands.json"

    response = session.get(start_url)
    all_poi = json.loads(response.text)

    for poi in all_poi:
        store_url = poi["yext_url"]
        store_url = (
            f'https://locations.dutchbros.com/dutch-bros-coffee-{poi["yext_url"]}'
            if store_url
            else ""
        )
        location_name = poi["store_nickname"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["stand_address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["store_number"]
        store_number = store_number if store_number else "<MISSING>"
        phone = ""
        if store_url:
            loc_response = session.get(store_url)
            if loc_response.status_code == 200:
                loc_dom = etree.HTML(loc_response.text)
                phone = loc_dom.xpath('//a[@data-pages-analytics="phonecall"]/text()')
                phone = phone[0] if phone else "<MISSING>"
        location_type = ""
        if poi["drivethru"] == "1":
            location_type = "drivethru"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lon"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["hours"]
        if not hours_of_operation:
            continue

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
