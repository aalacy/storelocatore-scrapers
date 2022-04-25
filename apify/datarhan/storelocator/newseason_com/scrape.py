import re
import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_usa


def fetch_data():
    session = SgRequests()
    start_url = "https://www.newseason.com/treatment-center-locations/"
    domain = "newseason.com"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//select[@id="DDLState"]/option/@value')
    for url in all_states:
        if url == "0":
            continue
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//li/a[contains(text(), "Learn More")]/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath("//h1/text()")[0]
            raw_address = loc_dom.xpath(
                '//div[@class="locContact"]/div[@class="section"]/text()'
            )
            for e in ["Bldg", "Suit", "Ste", "Unit", "Hwy"]:
                if e in raw_address[1]:
                    raw_address = [" ".join(raw_address[:2])] + [raw_address[2]]
            raw_address = raw_address[:2]
            raw_address = " ".join(
                ", ".join([e.strip() for e in raw_address if e.strip()]).split()
            )
            addr = parse_address_usa(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = loc_dom.xpath(
                '//div[@class="locContact"]//a[contains(@href, "tel")]/text()'
            )[0]
            geo = re.findall("mapCenter = (.+?);", loc_response.text)[0]
            geo = demjson.decode(geo)
            hoo = loc_dom.xpath(
                '//h4[contains(text(), "Business Hours")]/following-sibling::div//text()'
            )
            hoo = " ".join(hoo).split("New Hours")[0].split("Holidays")[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo["lat"],
                longitude=geo["lng"],
                hours_of_operation=hoo,
                raw_address=raw_address,
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
