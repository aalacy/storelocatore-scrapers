# -*- coding: utf-8 -*-
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

    start_url = "https://www.sylvanlearning.com/locations/"
    domain = "sylvanlearning.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//ul[@class="states smallList"]/li/a/@href')
    for url in all_states:
        url = urljoin(start_url, url)
        response = session.get(url, headers=hdr)
        if response.status_code != 200:
            continue
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//h2[@itemprop="name"]/a')
        for l_html in all_locations:
            page_url = l_html.xpath("@href")[0]
            location_name = l_html.xpath("text()")[0]
            loc_response = session.get(page_url, headers=hdr)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)

            street_address = loc_dom.xpath(
                '//div[div[@itemprop="streetAddress"]]/div/text()'
            )[:3]
            street_address = " ".join(
                [e.strip() for e in street_address if e.strip() and e.strip() != ","]
            )
            if not street_address:
                street_address = loc_dom.xpath(
                    '//span[@itemprop="streetAddress"]/text()'
                )
                if not street_address:
                    continue
                street_address = street_address[0]
            street_address = street_address.replace("Offering Online Programs", "")
            city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
            city = city[0] if city else ""
            state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
            state = state[0] if state else ""
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else ""
            geo = re.findall(r"LatLng\((.+?)\)", loc_response.text)
            latitude = ""
            longitude = ""
            if geo:
                geo = geo[0].split(", ")
                latitude = geo[0]
                longitude = geo[1]
            phone = loc_dom.xpath('//a[@aria-label="Click to Call"]/text()')[0].strip()
            hoo = loc_dom.xpath('//meta[@itemprop="openingHours"]/@content')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            if "/int" in page_url:
                country_code = url.split("country=")[-1].split("&")[0]
            else:
                country_code = page_url.split("/")[3]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
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
