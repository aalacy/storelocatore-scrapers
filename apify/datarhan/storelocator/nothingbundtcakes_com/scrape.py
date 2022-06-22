import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "nothingbundtcakes.com"

    start_url = "https://www.nothingbundtcakes.com/bakeries?"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[button[contains(text(), "View Bakery Information")]]/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        latitude = re.findall('latitude = "(.+?)";', loc_response.text)[0]
        longitude = re.findall('longitude = "(.+?)";', loc_response.text)[0]
        location_name = re.findall('name = "(.+?)";', loc_response.text)[0]
        street_address = re.findall('street = "(.+?)";', loc_response.text)[0]
        street_address_2 = re.findall('street2 = "(.+?)";', loc_response.text)
        if street_address_2:
            street_address += ", " + street_address_2[0]
        city = re.findall('city = "(.+?)";', loc_response.text)[0]
        state = re.findall('region_id = "(.+?)";', loc_response.text)[0]
        zip_code = re.findall('postcode = "(.+?)";', loc_response.text)[0]
        country_code = re.findall('country = "(.+?)";', loc_response.text)[0]
        store_number = re.findall('entity_id = "(.+?)";', loc_response.text)[0]
        phone = loc_dom.xpath('//a[@class="result-phone"]/text()')[0]
        hoo = loc_dom.xpath('//div[h4[contains(text(), "HOURS OF OPERATION")]]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()][1:])

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
            location_type="",
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
