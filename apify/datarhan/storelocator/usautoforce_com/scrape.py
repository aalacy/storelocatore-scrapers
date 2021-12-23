from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "usautoforce.com"
    start_url = "http://www.usautoforce.com/about/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@data-id]")
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="larger uppercase"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi_html.xpath('.//div[@class="map-location-button"]/div/text()')[
            1:
        ]
        city = address_raw[-1].split(", ")[0]
        street_address = address_raw[0]
        state = address_raw[-1].split(", ")[-1].split()[0]
        zip_code = address_raw[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        if poi_html.xpath("@class")[0].endswith("red"):
            location_type = "Tire's Warehouse"
        else:
            location_type = "U.S. AutoForce"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
