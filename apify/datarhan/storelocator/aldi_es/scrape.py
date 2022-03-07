from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.yellowmap.de/partners/AldiNord/Html/Poi.aspx"
    domain = "aldi.es"

    start_url = "https://www.aldi.es/supermercados/encuentra-tu-supermercado.html"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_cities = dom.xpath('//div[@class="mod-stores__multicolumn"]/p/a/@href')
    for url in all_cities:
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@data-t-name="stores"]//p/a/@href')
        for page_url in all_locations:
            page_url = urljoin(start_url, page_url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//p[@itemprop="name"]/text()')[0]
            street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[
                0
            ].strip()
            city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
            hoo = loc_dom.xpath(
                '//div[@class="mod-stores__overview-openhours"]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=zip_code,
                country_code="ES",
                store_number=SgRecord.MISSING,
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
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
