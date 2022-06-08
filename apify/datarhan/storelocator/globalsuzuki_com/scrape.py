# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.globalsuzuki.com/globallinks/"
    domain = "globalsuzuki.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    countries = [
        "Suriname",
        "Bhutan",
        "Cambodia",
        "Egypt",
        "Seychelles",
        "Democratic Republic of Timor-Leste",
        "Fiji",
        "French Polynesia",
        "Papua New Guinea",
        "Republic of Palau",
        "Kenya",
    ]

    for country_code in countries:
        poi_html = dom.xpath(
            f'//h1[contains(text(), "{country_code}")]/following-sibling::ul/li[@class="car"]'
        )[0]
        location_name = poi_html.xpath("text()")[0].strip()[1:]
        raw_address = poi_html.xpath('.//span[contains(text(), "Address")]/text()')
        zip_code = ""
        city = ""
        street_address = ""
        if raw_address:
            addr = parse_address_intl(raw_address[0].replace("Address : ", ""))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            city = addr.city
            zip_code = addr.postcode
        phone = [
            e
            for e in poi_html.xpath('.//span[contains(text(), "Address")]/text()')
            if "phone" in e.lower()
        ]
        phone = (
            " ".join(phone[0].split(":")[-1].strip().split()).split("/")[0]
            if phone
            else ""
        )
        hoo = ""
        if not phone:
            phone = (
                poi_html.xpath('.//span[contains(text(), "Phone")]/text()')[0]
                .split(":")[-1]
                .replace("\u3000", " ")
                .split()[0]
            )
            hoo = (
                poi_html.xpath('.//span[contains(text(), "Phone")]/text()')[0]
                .split(":")[-1]
                .replace("\u3000", " ")
                .split("(")[-1][:-1]
            )
        phone = phone.split(" 2482")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=", ".join(raw_address)
            .split("Phone")[0]
            .replace("Address : ", "")
            .strip(),
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
