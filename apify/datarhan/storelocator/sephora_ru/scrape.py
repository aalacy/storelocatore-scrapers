from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://sephora.ru/company/shops/"
    domain = "sephora.ru"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//div[@class="b-shops-cities__item"]/a/@href')
    for url in all_cities:
        city_url = urljoin(start_url, url)
        response = session.get(city_url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[div[@class="b-shops__slider-item-city"]]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(
                './/div[@class="b-shops__slider-item-name"]/text()'
            )[0].strip()
            street_address = (
                poi_html.xpath('.//div[@class="b-shops__slider-item-contacts"]/text()')[
                    0
                ]
                .split(":")[-1]
                .strip()
                .replace("\xa0", " ")
                .strip()
            )
            city = poi_html.xpath('.//div[@class="b-shops__slider-item-city"]/text()')[
                0
            ].strip()
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0].strip()
            geo = poi_html.xpath("@data-coords")[0][1:-1].split(",")
            raw_hoo = poi_html.xpath(
                './/div[@class="b-shops__slider-item-contacts"]//text()'
            )
            raw_hoo = " ".join([e.strip() for e in raw_hoo if e.strip()])
            hoo = raw_hoo.split("Открыто:")[-1].strip()

            item = SgRecord(
                locator_domain=domain,
                page_url=city_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code="RU",
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=geo[0],
                longitude=geo[-1],
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
