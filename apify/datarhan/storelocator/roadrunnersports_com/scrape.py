import re
import json
from lxml import etree

from sgrequests import SgRequests


def fetch_data():
    session = SgRequests()
    domain = "roadrunnersports.com"
    start_urls = [
        "https://stores.roadrunnersports.com/ca/",
        "https://stores.roadrunnersports.com/wa/",
        "https://stores.roadrunnersports.com/or/",
        "https://stores.roadrunnersports.com/az/",
        "https://stores.roadrunnersports.com/co/",
        "https://stores.roadrunnersports.com/il/",
        "https://stores.roadrunnersports.com/oh/",
        "https://stores.roadrunnersports.com/ga/",
        "https://stores.roadrunnersports.com/va/",
        "https://stores.roadrunnersports.com/md/",
        "https://stores.roadrunnersports.com/pa/",
        "https://stores.roadrunnersports.com/nj/",
    ]

    for url in start_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')

        for page_url in all_locations:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath(
                '//div[@class="col-8 map-list-item-address mt-10 mb-10"]/span/text()'
            )

            store_url = loc_dom.xpath(
                '//div[@class="col map-list-item-info mt-10 mb-10"]/a/@href'
            )[0]
            location_name = loc_dom.xpath(
                '//h2[@class="map-list-item-name-secondary text-uppercase"]/text()'
            )
            location_name = [elem.strip() for elem in location_name]
            location_name = " ".join(location_name)
            street_address = raw_address[0]
            city = raw_address[-1].split(", ")[0]
            state = raw_address[-1].split(", ")[-1].split()[0]
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
            store_number = loc_dom.xpath("//@data-fid")
            store_number = store_number[0] if store_number else ""
            phone = loc_dom.xpath('//a[@alt="Call Store"]/strong/text()')
            phone = phone[0] if phone else ""
            latitude = re.findall(r'lat":(.+?),', loc_response.text)[0]
            longitude = re.findall(r'lng":(.+?),', loc_response.text)[0]
            hours_of_operation = []
            hoo = loc_dom.xpath('//script[contains(text(), "primary =")]/text()')[0]
            hoo = re.findall("primary = (.+?);", hoo)[0]
            hoo = json.loads(hoo)
            for day, hours in hoo["days"].items():
                if hours != "closed":
                    opens = hours[0]["open"]
                    closes = hours[0]["close"]
                    hours_of_operation.append(f"{day} {opens} - {closes}")
                else:
                    hours_of_operation.append(f"{day} closed")
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number=store_number,
                phone=phone,
                location_type="",
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
