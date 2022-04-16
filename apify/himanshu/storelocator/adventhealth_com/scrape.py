import re
from lxml import etree
from urllib.parse import urljoin
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    start_url = "https://www.adventhealth.com/find-a-location"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="facility-search-block__item"]')
    next_page = dom.xpath('//a[@rel="next"]/@href')

    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//li[@class="facility-search-block__item"]')
        next_page = dom.xpath('//a[@rel="next"]/@href')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h3/a/@href")
        if not store_url:
            store_url = poi_html.xpath('.//a[contains(text(), "View Website")]/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        if store_url == "<MISSING>":
            store_url = "https://www.adventhealth.com/find-a-location"
        if "adventhealth.com" in store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath(
                '//span[@class="location-bar__name-text notranslate"]/text()'
            )
            if not location_name:
                location_name = loc_dom.xpath(
                    '//h1[@class="image-hero__title"]//text()'
                )
            location_name = [e.strip() for e in location_name if e.strip()]
            location_name = " ".join(location_name) if location_name else "<MISSING>"
            if location_name.endswith(","):
                location_name = location_name[:-1]
            street_address = loc_dom.xpath('//span[@property="streetAddress"]/text()')
            street_address = (
                street_address[0].strip() if street_address else "<MISSING>"
            )
            if street_address.endswith(","):
                street_address = street_address[:-1]
            city = loc_dom.xpath('//span[@property="addressLocality"]/text()')
            city = city[0] if city else "<MISSING>"
            state = loc_dom.xpath('//span[@property="addressRegion"]/text()')
            state = state[0] if state else "<MISSING>"
            zip_code = loc_dom.xpath('//span[@property="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = re.findall('country":"(.+?)",', loc_response.text)
            country_code = country_code[0] if country_code else "<MISSING>"
            phone = loc_dom.xpath('//a[@class="telephone"]/text()')
            phone = phone[0].strip() if phone and phone[0].strip() else "<MISSING>"
            latitude = loc_dom.xpath("//@data-lat")
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = loc_dom.xpath("//@data-lng")
            longitude = longitude[0] if longitude else "<MISSING>"
            hoo = loc_dom.xpath(
                '//div[@class="location-block__office-hours-hours"]/text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
            if hours_of_operation == "Please call for hours.":
                hours_of_operation = "<MISSING>"
        else:
            location_name = poi_html.xpath(".//h3/a/text()")
            if not location_name:
                location_name = poi_html.xpath(".//h3/text()")
            location_name = location_name[0].strip() if location_name else "<MISSING>"
            street_address = poi_html.xpath('.//span[@property="streetAddress"]/text()')
            street_address = (
                street_address[0].strip() if street_address else "<MISSING>"
            )
            city = poi_html.xpath('.//span[@property="addressLocality"]/text()')
            city = city[0] if city else "<MISSING>"
            state = poi_html.xpath('.//span[@property="addressRegion"]/text()')
            state = state[0] if state else "<MISSING>"
            zip_code = poi_html.xpath('.//span[@property="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = re.findall('country":"(.+?)",', loc_response.text)
            country_code = country_code[0] if country_code else "<MISSING>"
            phone = poi_html.xpath('.//a[@class="telephone"]/text()')
            phone = phone[0].strip() if phone and phone[0].strip() else "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
