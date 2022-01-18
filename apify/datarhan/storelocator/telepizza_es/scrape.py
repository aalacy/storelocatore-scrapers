import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.telepizza.es/pizzerias"
    domain = "telepizza.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_areas = dom.xpath('//ul[@class="areas"]/li/a/@href')
    for url in all_areas:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//ul[@class="cities"]/li/a/@href')
        for url in all_cities:
            url = urljoin(start_url, url)
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//ul[@class="list"]/li')
            for poi_html in all_locations:
                page_url = poi_html.xpath('.//a[@class="moreInfoLinkFromList"]/@href')
                if not page_url:
                    page_url = poi_html.xpath("//@urltienda")
                page_url = urljoin(start_url, page_url[0])
                loc_response = session.get(page_url)
                if loc_response.status_code != 200:
                    continue
                loc_dom = etree.HTML(loc_response.text)

                location_name = poi_html.xpath(".//h2/text()")[0]
                raw_address = poi_html.xpath('.//p[@class="prs"]/text()')
                zip_code = loc_dom.xpath("//address/span[2]/text()")[0]
                city = raw_address[-1]
                if city.startswith("."):
                    city = city[1:]
                phone = poi_html.xpath('.//p[span[@class="i_phone"]]/span[2]/text()')[0]
                latitude = re.findall("lat = (.+?);", loc_response.text)[0]
                longitude = re.findall("lng = (.+?);", loc_response.text)[0]
                hoo = loc_dom.xpath(
                    '//h4[contains(text(), "A recoger")]/following-sibling::table//text()'
                )
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=city,
                    state="",
                    zip_postal=zip_code,
                    country_code="ES",
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
