from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://restaurants.fiveguys.de/index.html"
    domain = "fiveguys.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for url in all_urls:
        if len(url.split("/")) > 1:
            all_locations.append(url)
            continue
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//a[span[contains(text(), "Mehr herausfinden")]]/@href'
        )

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath(
            '//span[@class="LocationName"]/span[@class="LocationName-geo"]/text()'
        )[0]
        street_address = loc_dom.xpath(
            '//div[@class="Core-address"]//span[@class="c-address-street-1"]/text()'
        )[0]
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
        country_code = loc_dom.xpath("//@data-country")[0]
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else ""
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        phone = loc_dom.xpath('//div[@itemprop="telephone"]/text()')[0]
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
