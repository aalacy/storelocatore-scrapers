from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "schlotzskys.com"

    start_url = "https://locations.schlotzskys.com/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = []
    all_states = dom.xpath('//a[@class="Directory-listLink"]')
    for state in all_states:
        url = urljoin(start_url, state.xpath("@href")[0])
        count = state.xpath("@data-count")[0]
        if count[1:-1] == "1":
            all_locations.append(url)
            continue
        response = session.get(url, headers=hdr)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//a[@class="Directory-listLink"]')
        all_locations += dom.xpath('//a[@data-ya-track="visitpage"]/@href')
        for city in all_cities:
            url = urljoin(start_url, city.xpath("@href")[0])
            count = city.xpath("@data-count")[0]
            if count[1:-1] == "1":
                all_locations.append(url)
                continue
            response = session.get(url, headers=hdr)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@data-ya-track="visitpage"]/@href')

    for url in list(set(all_locations)):
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        com_soon = loc_dom.xpath('//span[contains(text(), "Coming Soon")]')
        if com_soon:
            continue
        location_name = loc_dom.xpath('//h2[@class="Core-title"]/text()')
        if not location_name:
            location_name = loc_dom.xpath('//span[@class="Hero-geo"]/a/text()')
        location_name = location_name[0]
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')[0]
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = loc_dom.xpath("//@data-country")[0]
        phone = loc_dom.xpath('//div[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else ""
        location_type = loc_dom.xpath("//main/@itemtype")[0].split("/")[-1]
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath('//table[@class="c-hours-details"]//text()')[2:]
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)
        store_number = loc_dom.xpath('//a[contains(@href, "store_code")]/@href')
        store_number = store_number[0].split("=")[-1] if store_number else ""

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
            location_type=location_type,
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
