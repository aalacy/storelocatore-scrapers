from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests()

    domain = "dxl.com"
    start_urls = ["https://stores.dxl.com/us", "https://stores.dxl.com/ca"]

    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_states = dom.xpath('//a[@class="Directory-listLink"]')
        all_locations = []
        for state in all_states:
            url = urljoin(start_url, state.xpath("@href")[0])
            count = int(state.xpath("@data-count")[0][1:-1])
            if count == 1:
                all_locations.append(url)
                continue
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_cities = dom.xpath('//a[@class="Directory-listLink"]')
            for city in all_cities:
                url = urljoin(start_url, city.xpath("@href")[0])
                count = int(city.xpath("@data-count")[0][1:-1])
                if count == 1:
                    all_locations.append(url)
                    continue
                response = session.get(url)
                dom = etree.HTML(response.text)
                all_locations += dom.xpath(".//@data-location-link")

        for url in all_locations:
            store_url = urljoin(start_url, url)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = " ".join(
                loc_dom.xpath('//span[@id="location-name"]//text()')
            )
            street_address = loc_dom.xpath(
                '//meta[@itemprop="streetAddress"]/@content'
            )[0]
            city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
            state = loc_dom.xpath(
                '//div[@class="Core-address"]//abbr[@class="c-address-state"]/text()'
            )[0]
            zip_code = loc_dom.xpath(
                '//div[@class="Core-address"]//span[@itemprop="postalCode"]/text()'
            )[0]
            country_code = loc_dom.xpath("//@data-country")[0]
            phone = loc_dom.xpath('//div[@itemprop="telephone"]/text()')[0]
            latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
            longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
            hoo = loc_dom.xpath(
                '//div[@class="Core-hours js-Core-hours"]//table[@class="c-hours-details"]/tbody//text()'
            )
            hours_of_operation = " ".join(hoo) if hoo else SgRecord.MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
