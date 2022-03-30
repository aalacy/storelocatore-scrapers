from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "hobbycraft.co.uk"
    start_url = "https://www.hobbycraft.co.uk/storelist/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="b-storelocator_locations-item_location"]/a/@href'
    )

    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h1[@class="b-storelocator_result-title"]/text()'
        )[0].strip()
        raw_address = loc_dom.xpath(
            '//div[@class="b-storelocator_result"]//div[@class="b-storelocator_result-address"]/p/text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if len(raw_address) == 4:
            street_address = " ".join(raw_address[:2])
        else:
            street_address = raw_address[0]
        city = loc_dom.xpath(
            '//div[@class="b-storelocator_result"]//p[@class="b-storelocator_result-city"]/text()'
        )[0]
        zip_code = loc_dom.xpath(
            '//div[@class="b-storelocator_result"]//p[@class="b-storelocator_result-postalcode"]/text()'
        )[0]
        phone = loc_dom.xpath(
            '//div[@class="b-storelocator_result"]//a[@class="b-link_phone m-simple"]/text()'
        )[-1].strip()
        hoo = loc_dom.xpath(
            '//div[@class="b-storelocator_result"]//div[@class="b-accordion-content_inner b-storelocator_result-schedule_content"]//td/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="UK",
            store_number="",
            phone=phone,
            location_type="",
            latitude=loc_dom.xpath("//@data-latitude")[0],
            longitude=loc_dom.xpath("//@data-longitude")[0],
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
