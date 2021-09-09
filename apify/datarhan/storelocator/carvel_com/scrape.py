from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "carvel.com"
    user_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }

    all_locations = []
    start_url = "https://locations.carvel.com"
    response = session.get(start_url, headers=user_agent)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//a[@class="Directory-listLink"]')
    for u in all_urls:
        url = u.xpath("@href")[0]
        count = u.xpath("@data-count")[0]
        if count == "(1)":
            all_locations.append(url)
            continue
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_sub = dom.xpath('//a[@class="Directory-listLink"]')
        for u in all_sub:
            s_url = u.xpath("@href")[0]
            count = u.xpath("@data-count")[0]
            if count == "(1)":
                all_locations.append(s_url)
                continue
            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@class="Link Link--primary"]/@href')

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//a[@class="Hero-geoText"]/text()')[0]
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')[0]
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else ""
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = loc_dom.xpath("//@data-country")[0]
        phone = loc_dom.xpath('//div[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else ""
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath('//table[@class="c-hours-details"]//text()')[2:]
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
