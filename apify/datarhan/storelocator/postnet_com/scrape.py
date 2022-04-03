import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "postnet.com"
    start_url = "https://locations.postnet.com/search?q={}"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)

        all_urls = dom.xpath(
            '//ol[@class="ResultList"]/li//a[@class="Teaser-titleLink"]/@href'
        )
        for url in all_urls:
            store_url = "https://locations.postnet.com/" + url
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)

            location_name = " ".join(store_dom.xpath(".//h1//text()"))
            location_name = location_name if location_name else "<MISSING>"
            street_address = store_dom.xpath(
                '//meta[@itemprop="streetAddress"]/@content'
            )
            street_address = street_address[0] if street_address else "<MISSING>"
            city = store_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
            city = city[0] if city else "<MISSING>"
            state = store_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
            state = state[0] if state else "<MISSING>"
            zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = store_dom.xpath("//address/@data-country")
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = store_dom.xpath('//span[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = store_dom.xpath('//meta[@itemprop="latitude"]/@content')
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = store_dom.xpath('//meta[@itemprop="longitude"]/@content')
            longitude = longitude[0] if longitude else "<MISSING>"
            hours_of_operation = []
            hours = store_dom.xpath("//div/@data-days")[0]
            hours = json.loads(hours)
            for elem in hours:
                if elem["intervals"]:
                    end = str(elem["intervals"][0]["end"])[:2] + ":00"
                    start = str(elem["intervals"][0]["start"])[:2] + ":00"
                    hours_of_operation.append(
                        "{} {} - {}".format(elem["day"], start, end)
                    )
                else:
                    hours_of_operation.append("{}  closed".format(elem["day"]))
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
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
