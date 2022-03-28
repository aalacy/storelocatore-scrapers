# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "tommybahama.com"
    start_url = "https://www.tommybahama.com/restaurants-and-marlin-bars/locations"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[@restaurant-feature-item]/a/@href")
    for url in list(set(all_locations)):
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        page_url = loc_dom.xpath('//a[contains(text(), "Store Information")]/@href')
        if page_url:
            page_url = page_url[0]
            if "http" not in page_url:
                page_url = urljoin(start_url, page_url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
        else:
            continue

        raw_data = loc_dom.xpath(
            '//p[b[contains(text(), "Store")]]/following-sibling::p/text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//div[@class="store-details-container mt-30"]/div[1]/text()'
            )[:-1]
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//p[contains(text(), "Store")]/following-sibling::p/text()'
            )
        raw_data = [
            e.replace("\xa0", " ").strip()
            for e in raw_data
            if e.strip() and e != "\xa0"
        ]
        raw_address = [
            e
            for e in raw_data
            if "Open" not in e
            and "Phone" not in e
            and "AM -" not in e
            and not e.endswith("PM")
        ]
        if (
            len(raw_address[0].split(".")) == 3
            and raw_address[0].split(".")[1].strip().isdigit()
        ):
            raw_address = raw_address[1:]
        addr = parse_address_intl(" ".join(raw_address))
        location_name = loc_dom.xpath('//h3[@class="cmp-title__text"]/text()')
        if not location_name:
            location_name = loc_dom.xpath("//h1/text()")
        if not location_name:
            continue
        location_name = location_name[0]
        street_address = raw_address[0]
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = ""
        if zip_code and len(zip_code) == 5:
            country_code = "United States"
        phone = loc_dom.xpath(
            '//p[b[contains(text(), "Store")]]/following-sibling::p/b/text()'
        )
        if not phone:
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        if not phone:
            phone = [e.replace("Phone:", "") for e in raw_data if "Phone:" in e]
        if not phone:
            phone = loc_dom.xpath(
                '//p[b[contains(text(), "Store")]]/following-sibling::p/text()'
            )
        if not phone:
            phone = loc_dom.xpath(
                '//p[contains(text(), "Store")]/following-sibling::p/text()'
            )
        phone = phone[0].split(":")[-1].strip()
        hoo = loc_dom.xpath(
            '//p[contains(text(), "Open:")]/following-sibling::p[1]/text()'
        )
        hoo_2 = loc_dom.xpath(
            '//p[contains(text(), "Open:")]/following-sibling::p[2]/text()'
        )
        if hoo_2 and "Fri-" in hoo_2[0]:
            hoo.append(hoo_2[0])
        if hoo and "Open to a limited number" in hoo[0]:
            hoo = ""
        if not hoo:
            hoo = loc_dom.xpath(
                '//p[descendant::b[contains(text(), "Store")]]/following-sibling::p[contains(text(), "Open:")]/text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[contains(text(), "Store Hours")]/following-sibling::div/text()'
            )
        if not hoo:
            hoo = [e.replace("Open:", "") for e in raw_data if "Open:" in e]
        hoo = [
            e.replace("Hours:", "").replace("Hours", "").strip()
            for e in hoo
            if e.strip() and "Order online" not in e
        ]
        hoo = (
            " ".join(hoo)
            .split("This")[0]
            .split("Open to a limited")[0]
            .replace(">br>", "")
            .split("Reservations Encouraged. ")[-1]
            .replace("ours:", "")
            .strip()
        )

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
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=" ".join(raw_address),
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
