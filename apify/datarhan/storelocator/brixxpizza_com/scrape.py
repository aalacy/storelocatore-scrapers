import json
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    domain = "brixxpizza.com"
    start_url = "https://brixxpizza.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//a/@data-id")

    for loc_id in all_locations:
        url = "https://brixxpizza.com/wp-content/themes/Brixxpizza/inner-ajax.php"
        formdata = {"id": loc_id}
        loc_response = session.post(url, data=formdata)
        loc_dom = etree.HTML(loc_response.text)

        store_url = loc_dom.xpath('//a[contains(text(), "view details")]/@href')[0]
        location_name = loc_dom.xpath("//h3/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@data-yext-field="address1"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@data-yext-field="city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@data-yext-field="state"]/text()')
        state = state[0] if state else "<MISSING>"
        state = state.split("-")[-1]
        zip_code = loc_dom.xpath('//span[@data-yext-field="zip"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = loc_id
        phone = loc_dom.xpath('//a[@data-yext-field="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="frankin-date"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"
        latitude = ""
        longitude = ""
        with SgFirefox() as driver:
            driver.get(store_url)
            sleep(15)
            loc_dom = etree.HTML(driver.page_source)
            poi = loc_dom.xpath('//script[@class="yext-schema-json"]/text()')
            if poi:
                poi = json.loads(poi[0])
                latitude = poi["geo"]["latitude"]
                longitude = poi["geo"]["longitude"]

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
