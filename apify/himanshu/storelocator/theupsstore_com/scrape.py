# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://locations.theupsstore.com/"
    domain = "theupsstore.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//a[@data-ya-track="dir_link"]/@href')
    all_cities = []
    all_locations = []
    for url in all_states:
        if len(url) > 2:
            all_cities.append(url)
        else:
            url = urljoin(start_url, url)
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_cities = dom.xpath('//a[@data-ya-track="dir_link"]/@href')
            for url in all_cities:
                if len(url.split("/")) == 2:
                    url = urljoin(start_url, url)
                    response = session.get(url)
                    dom = etree.HTML(response.text)
                    all_locations += dom.xpath('//a[@data-ya-track="viewpage"]/@href')
                else:
                    all_locations.append(url)

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//div[contains(text(), "Coming Soon")]'):
            continue
        location_name = loc_dom.xpath(
            '//h1[@id="location-name"]/span[@class="LocationName"]/span/text()'
        )
        location_name = " ".join(location_name)
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')[0]
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else ""
        country_code = loc_dom.xpath("//@data-country")[0]
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath('//table[@class="c-hours-details"]//text()')[3:]
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
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
