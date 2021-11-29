from lxml import etree
from urllib.parse import urljoin

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests


def fetch_data():
    session = SgRequests()

    domain = "nationwide.com"
    start_url = "https://agency.nationwide.com/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//a[@class="Directory-listLink"]')
        for city in all_cities:
            url = city.xpath("@href")[0]
            response = session.get(urljoin(start_url, url))
            code = response.status_code
            while code != 200:
                session = SgRequests()
                response = session.get(urljoin(start_url, url))
                code = response.status_code
            dom = etree.HTML(response.text)

            all_locations = dom.xpath('//a[h3[@id="location-name"]]/@href')
            for url in all_locations:
                store_url = urljoin(start_url, url)
                loc_response = session.get(store_url)
                loc_dom = etree.HTML(loc_response.text)

                location_name = loc_dom.xpath('//h1/span[@itemprop="name"]/text()')[0]
                street_address = loc_dom.xpath(
                    '//span[@class="c-address-street-1"]/text()'
                )[0]
                str_2 = loc_dom.xpath('//span[@class="c-address-street-2"]/text()')
                if str_2:
                    street_address += " " + str_2[0]
                city = loc_dom.xpath('//span[@class="c-address-city"]/text()')[0]
                state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')[0]
                zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
                country_code = loc_dom.xpath("//@data-country")[0]
                phone = loc_dom.xpath('//span[@id="telephone"]/text()')
                phone = phone[0] if phone else SgRecord.MISSING
                latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
                longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
                hoo = loc_dom.xpath(
                    '//table[@class="c-location-hours-details"]//text()'
                )[2:]
                hoo = [e.strip() for e in hoo if e.strip()]
                hours_of_operation = " ".join(hoo) if hoo else SgRecord.MISSING

                yield SgRecord(
                    store_number=SgRecord.MISSING,
                    page_url=store_url,
                    location_name=location_name,
                    location_type=SgRecord.MISSING,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    phone=phone,
                    locator_domain=domain,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
