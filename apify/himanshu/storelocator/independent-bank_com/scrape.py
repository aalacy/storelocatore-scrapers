from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://locations.ifinancial.com/index.html"
    domain = "ifinancial.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for url in all_states:
        response = session.get(urljoin(start_url, url), headers=hdr)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//a[@class="Directory-listLink"]')
        for city in all_cities:
            count = city.xpath("@data-count")[0][1:-1]
            url = city.xpath("@href")[0]
            if count == "1":
                all_locations.append(url)
                continue

            response = session.get(urljoin(start_url, url), headers=hdr)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@class="Teaser-titleLink"]/@href')

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@class="LocationName-geo"]/text()')[0]
        street_address = loc_dom.xpath(
            '//span[@class="Address-field Address-line1"]/text()'
        )[0]
        city = loc_dom.xpath('//span[@class="Address-field Address-city"]/text()')[0]
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = loc_dom.xpath("//@data-country")[0]
        phone = loc_dom.xpath(
            '//div[@class="Phone Hero-phone"]//span[@itemprop="telephone"]/text()'
        )
        phone = phone[0] if phone else SgRecord.MISSING
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        if "ATM" in location_name:
            hoo = loc_dom.xpath(
                '//div[h2[contains(text(), "ATM Hours")]]//table[@class="c-hours-details"]/tbody//text()'
            )
            location_type = "ATM"
        else:
            hoo = loc_dom.xpath(
                '//div[h2[contains(text(), "Lobby Hours")]]//table[@class="c-hours-details"]/tbody//text()'
            )
            location_type = "BRANCH"
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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
