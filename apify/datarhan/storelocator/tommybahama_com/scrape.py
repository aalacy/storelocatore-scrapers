# -*- coding: utf-8 -*-
import re
from lxml import etree
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "tommybahama.com"
    start_url = "https://www.tommybahama.com/en/store-finder?q=&searchStores=on&searchOutlets=on"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View Store")]/@href')
    next_page = dom.xpath('//a[contains(text(), "Next")]/@href')[0]
    next_page = urljoin(start_url, next_page)
    total_pages = dom.xpath('//ul[@class="pager"]/li/p/text()')[0].split()[-1]
    for p in range(1, int(total_pages)):
        next_url = add_or_replace_parameter(next_page, "page", str(p))
        response = session.get(next_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(text(), "View Store")]/@href')

    for url in list(set(all_locations)):
        if "/store/" not in url:
            continue
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        latitude = re.findall("storelatitude = '(.+?)';", loc_response.text)[0]
        longitude = re.findall("storelongitude = '(.+?)';", loc_response.text)[0]
        location_type = re.findall("storeType = '(.+?)';", loc_response.text)[0]
        street_address = re.findall("storeaddressline1 = '(.+?)';", loc_response.text)
        street_address = street_address[0] if street_address else ""
        city = re.findall("storeaddresstown = '(.+?)';", loc_response.text)[0]
        country_code = re.findall(
            "storeaddresscountryname = '(.+?)';", loc_response.text
        )
        country_code = country_code[0] if country_code else ""
        raw_data = loc_dom.xpath(
            '//div[@class="store-details-container mt-30"]/div/text()'
        )
        raw_data = [e.replace("\xa0", " ").strip() for e in raw_data if e.strip()]
        if "#" in raw_data[1]:
            raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
        if not street_address:
            street_address = raw_data[0]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        hoo = " ".join(raw_data)
        if "Hours:" in hoo:
            hoo = hoo.split("Hours:")[1].split("This")[0]
        else:
            hoo = hoo.split("Hours")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=raw_data[1].split(", ")[1].split()[0],
            zip_postal=raw_data[1].split(", ")[1].split()[1],
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
        )

        yield item

    response = session.get(
        "https://www.tommybahama.com/stores-restaurants/international-locations"
    )
    dom = etree.HTML(response.text)
    int_locations = dom.xpath('//p[a[u[contains(text(), "VIEW MAP")]]]')
    for poi_html in int_locations:
        raw_data = poi_html.xpath("text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        for i, e in enumerate(raw_data):
            if len(e.split(".")) > 2 and "(" not in e:
                index = i
                break
        raw_address = ", ".join(raw_data[1:index])
        addr = parse_address_intl(raw_address)
        hoo = " ".join(raw_data).split("Open")[-1].strip()
        if "am-" not in hoo.lower():
            hoo = ""
        phone = [e for e in raw_data if len(e.split(".")) > 2 and "," not in e]
        phone = phone[0] if phone else ""
        if "Dubai" in phone:
            phone = ""
        if "Brisbane" in phone:
            phone = ""
        country_code = addr.country
        zip_code = addr.postcode
        if zip_code and len(zip_code.split()) == 2 and not country_code:
            country_code = "Canada"
        if (zip_code and len(zip_code) == 5) and not country_code:
            country_code = "United States"
        if (zip_code and len(zip_code) < 5) and not country_code:
            country_code = "AU"
        location_name = raw_data[0]
        if not country_code and "Tommy Bahama" in location_name:
            country_code = "UNITED ARAB EMIRATES"
        latitude = ""
        longitude = ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.tommybahama.com/stores-restaurants/international-locations",
            location_name=location_name,
            street_address=raw_data[1],
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=raw_address,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
