import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://shipleydonuts.com/stores-html-sitemap/"
    domain = "shipleydonuts.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@href, "/stores/")]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url, headers=hdr)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="wpsl-locations-details"]//strong/text()'
        )[0]
        raw_address = loc_dom.xpath('//div[@class="wpsl-location-address"]/span/text()')
        if len(raw_address) == 6:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        latitude = re.findall('lat":"(.+?)",', loc_response.text)[0]
        longitude = re.findall('lng":"(.+?)","id"', loc_response.text)[0]
        hoo = loc_dom.xpath('//table[@class="wpsl-opening-hours"]//text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[2],
            zip_postal=raw_address[3],
            country_code=raw_address[-1],
            store_number=str(loc_response.url.raw[-1]).split("/")[-2],
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
