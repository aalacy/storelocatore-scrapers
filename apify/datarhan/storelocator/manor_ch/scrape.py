# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.manor.ch/store-finder/search"
    domain = "manor.ch"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_types = ["STORE", "SUPERMARKET", "RESTAURANT", "SANOVIT"]
    for location_type in all_types:
        frm = {"doSearch": True, "searchText": "", "shops": [location_type]}
        response = session.post(start_url, headers=hdr, json=frm)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[@class="m-store-list-item"]')
        for poi_html in all_locations:
            page_url = poi_html.xpath(".//a/@href")[0]
            page_url = urljoin(start_url, page_url)

            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi_html.xpath(
                './/span[@class="m-store-list-item__store__name"]/text()'
            )[0]
            raw_data = loc_dom.xpath(
                '//div[@class="m-store-details__storeinfo"]/span/text()'
            )[1:]
            raw_data = [e.strip() for e in raw_data if e.strip()]
            latitude = loc_dom.xpath('//input[@class="js-map-latitude"]/@value')
            latitude = latitude[0] if latitude else ""
            longitude = loc_dom.xpath('//input[@class="js-map-longitude"]/@value')
            longitude = longitude[0] if longitude else ""
            phone = [e.split(":")[-1].strip() for e in raw_data if "Telefon" in e]
            phone = phone[0] if phone else ""
            city = " ".join(raw_data[1].split()[1:])
            phone = phone.split(",")[0].strip()
            if city in phone:
                phone = ""
            if location_type == "RESTAURANT":
                hoo = loc_dom.xpath(
                    '//div[div[img[contains(@src, "store-manora-logo")]]]/following-sibling::ul[1]//text()'
                )
                if not hoo:
                    hoo = loc_dom.xpath(
                        '//div[div[img[contains(@src, "manora-fresh-to-go")]]]/following-sibling::ul[1]//text()'
                    )
                if not hoo:
                    hoo = loc_dom.xpath(
                        '//div[div[img[contains(@src, "manora-pasta-pizza")]]]/following-sibling::ul[1]//text()'
                    )
            if location_type == "SUPERMARKET":
                hoo = loc_dom.xpath(
                    '//div[div[img[contains(@src, "manor-food-logo")]]]/following-sibling::ul[1]//text()'
                )
            if location_type == "STORE":
                hoo = loc_dom.xpath(
                    '//div[div[img[contains(@src, "manor-logo")]]]/following-sibling::ul[1]//text()'
                )
            if not hoo:
                hoo = loc_dom.xpath(
                    '//ul[contains(@class, "details__shops__worktime__days")]//text()'
                )
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_data[0],
                city=city,
                state="",
                zip_postal=raw_data[1].split()[0],
                country_code="",
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
