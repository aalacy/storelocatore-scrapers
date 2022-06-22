# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.renault.co.ke/contact/dealerlist.html",
        "http://renault-ci.com/servicesrenault/nous-joindre.html",
        "https://www.renault.co.mz/contacto/caetano-mocambique.html",
        "https://www.renault.co.tz/contact/dealerlist.html",
        "http://www.renault.co.ug/contact/dealerlist.html",
        "http://www.renault.co.zm/contact/dealerlist.html",
    ]
    domain = "renault.co.ke"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//table[@class="dealers-list_table"]/tbody/tr')
        for poi_html in all_locations:
            location_name = poi_html.xpath(
                './/span[@class="dealers-list_arrowlink-text"]/text()'
            )[0]
            raw_address = poi_html.xpath("./td[1]/text()")
            raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = (
                poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
                .split(":")[-1]
                .split("/")[0]
            )
            hoo = dom.xpath(
                '//p[b[contains(text(), "OPENING TIMES")]]/following-sibling::p//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            location_type = " ".join(poi_html.xpath("./td[2]/span/@title")).replace(
                "<br>", ""
            )
            country_code = start_url.split("/")[2].split(".")[-1]
            if country_code == "com":
                country_code = "ci"

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude="",
                longitude="",
                hours_of_operation=hoo,
                raw_address=raw_address,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
