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

    start_url = "https://www.kumon.com.hk/zh-tw/"
    domain = "kumon.com.hk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    hdr = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36",
    }

    regions = dom.xpath('//select[@name="region_id"]/option/@value')[1:]
    for reg_id in regions:
        reg_url = "https://www.kumon.com.hk/zh-tw/be-a-student-4/index.php?option=com_centerdirectory&task=ajax.getAreaList&region_id={}&existOnly=1"
        all_areas = session.get(reg_url).json()
        for a in all_areas:
            frm = {
                "region_id": reg_id,
                "area_id": a["id"],
                "keywords": "",
                "submit": "搜尋",
            }
            post_url = "https://www.kumon.com.hk/zh-tw/be-a-student-4/center-search?view=centerlist"
            response = session.post(post_url, data=frm)
            dom = etree.HTML(response.text)

            all_locations = dom.xpath('//div[@class="center-list"]/div')
            for poi_html in all_locations:
                if len(str(etree.tostring(poi_html))) < 100:
                    continue
                if "center-map-bottom col-lg-12" in str(etree.tostring(poi_html)):
                    continue
                location_name = poi_html.xpath(
                    './/div[@class="center-name  col-lg-12"]/div[2]/text()'
                )[0]
                raw_address = poi_html.xpath(
                    './/div[@class="center-address col-lg-12"]/div[2]/text()'
                )[0].strip()
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                phone = poi_html.xpath(
                    './/div[@class="center-phone col-lg-12"]/div[2]/text()'
                )[0][:8].strip()
                geo = poi_html.xpath('.//button[@name="map"]/@onclick')[0].split(",")[
                    1:3
                ]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="",
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude=geo[0],
                    longitude=geo[1],
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
