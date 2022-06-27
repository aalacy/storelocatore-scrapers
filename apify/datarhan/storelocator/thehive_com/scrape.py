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

    start_url = "https://thehive.com/"
    domain = "thehive.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_countries = dom.xpath('//div[h2[a[@class="next_country"]]]')
    for c_html in all_countries:
        country_code = c_html.xpath(".//h2/text()")[0].strip()

        all_locations = c_html.xpath('.//div[@class="text_slide"]')
        for poi_html in all_locations:
            open_soon = poi_html.xpath(".//h4/text()")
            if open_soon and "Opening" in open_soon[0]:
                continue
            location_name = poi_html.xpath(".//h3/text()")[0]
            page_url = poi_html.xpath('.//a[contains(text(), "Find Out")]/@href')[0]
            loc_response = session.get(page_url + "/location/", headers=hdr)
            if (
                loc_response.status_code == 200
                and "attribution,zoompan.html?access_token" not in loc_response.text
            ):
                loc_dom = etree.HTML(loc_response.text)

                raw_address = loc_dom.xpath(
                    '//h3[contains(text(), "Address:")]/following-sibling::ul[1]//text()'
                )
                if not raw_address:
                    raw_address = loc_dom.xpath(
                        '//*[contains(text(), "Location")]/following-sibling::ul[1]/li/text()'
                    )
                raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
                phone = phone[0].split(": ")[-1] if phone else ""
                if not phone:
                    phone = loc_dom.xpath(
                        '//h4[contains(text(), "Contact")]/following-sibling::ul[1]/li/text()'
                    )[0]
                geo = (
                    loc_dom.xpath("//iframe/@src")[0]
                    .split("!2d")[-1]
                    .split("!2m3")[0]
                    .split("!3d")
                )
                latitude = geo[0].split("!")[0]
                longitude = geo[1].split("!")[0]
            else:
                loc_response = session.get(page_url, headers=hdr)
                loc_dom = etree.HTML(loc_response.text)

                raw_address = loc_dom.xpath(
                    '//h4[contains(text(), "Location")]/following-sibling::ul[1]//text()'
                )
                if not raw_address:
                    raw_address = loc_dom.xpath(
                        '//span[contains(text(), "Location")]/following-sibling::ul[1]/li/text()'
                    )
                if not raw_address:
                    raw_address = loc_dom.xpath(
                        '//h2[@id="location"]/following-sibling::p[1]/text()'
                    )
                raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
                phone = phone[0].split(": ")[-1] if phone else ""
                if not phone:
                    phone = loc_dom.xpath(
                        '//h4[contains(text(), "Contact")]/following-sibling::ul[1]/li/text()'
                    )[0]
                latitude = ""
                longitude = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state="",
                zip_postal=addr.postcode,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
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
