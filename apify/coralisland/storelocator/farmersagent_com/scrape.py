# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://agents.farmers.com/index.html"
    domain = "farmersagent.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = []
    all_states = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for url in all_states:
        if len(url.split("/")) == 3:
            all_locations.append(url)
            continue
        state_url = urljoin(start_url, url)
        response = session.get(state_url, headers=hdr)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//a[@class="Directory-listLink"]/@href')
        for url in all_cities:
            if len(url.split("/")) == 3:
                all_locations.append(url)
                continue
            city_url = urljoin(start_url, url)
            response = session.get(city_url, headers=hdr)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@class="Teaser-title-link"]/@href')

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@itemprop="name"]/text()')[0]
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')[0]
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = loc_dom.xpath("//@data-country")[0]
        phone = loc_dom.xpath('//div[@id="phone-main"]/text()')[0]
        geo = loc_dom.xpath('//meta[@name="geo.position"]/@content')[0].split(";")
        hoo = loc_dom.xpath('//table[@class="c-hours-details"]//text()')
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
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
