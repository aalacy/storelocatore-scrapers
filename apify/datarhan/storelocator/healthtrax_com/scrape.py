import re
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.healthtrax.com/locations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@data-type="page"]/div[3]//p[@style="white-space:pre-wrap;"]/a[strong]/@href'
    )
    for store_url in all_locations:
        store_url = urljoin(start_url, store_url)
        loc_response = session.get(store_url, headers=hdr)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)
        geo = loc_dom.xpath("//div/@data-block-json")
        if geo:
            geo = json.loads([e for e in geo if "addressCountry" in e][0])

        location_name = loc_dom.xpath("//h1/strong/text()")
        if not location_name:
            location_name = loc_dom.xpath('//h1[@class="text-align-center"]/text()')
        if not location_name:
            location_name = loc_dom.xpath('//div[@class="cmsPageContent"]/h1/text()')
        if not location_name:
            location_name = loc_dom.xpath("//div/h1/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//p[strong[contains(text(), "Location:")]]/text()')
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//div[h3[contains(text(), "WE ARE OPEN")]]/p[1]/text()'
            )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//p[strong[contains(text(), "Location:")]]/a/text()'
            )
            raw_address = [e.strip() for e in raw_address if e.strip()]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        if geo:
            country_code = geo["location"]["addressCountry"]
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            latitude = geo["location"]["mapLat"]
            longitude = geo["location"]["mapLng"]
        hoo = loc_dom.xpath(
            '//p[strong[contains(text(), "Hours of Operation: ")]]/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[@class="sqs-block-content"]/p[contains(text(), "am -")]/text()'
            )
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="ClearFix cmsPanelContent"]/p/text()')[
                2:10
            ]
        hoo = [" ".join([s.strip() for s in e.split()]) for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if hours_of_operation.startswith("Sunday"):
            hoo = loc_dom.xpath(
                '//div[p[strong[contains(text(), "Hours of Operation:")]]]//text()'
            )[1:5]
            hours_of_operation = " ".join(hoo)

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
