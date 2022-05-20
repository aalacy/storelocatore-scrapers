from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium.sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.aronarents.com/locations"
    domain = "aronarents.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    with SgFirefox() as driver:
        all_locations = dom.xpath('//div[@class="locations-item"]')
        for poi_html in all_locations:
            page_url = poi_html.xpath('.//a[contains(text(), "VIEW STORE")]/@href')[0]
            page_url = urljoin(start_url, page_url)
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)

            location_name = poi_html.xpath('.//div[@class="name"]/text()')
            location_name = location_name[0] if location_name else ""
            raw_address = poi_html.xpath('.//div[@class="address"]/text()')
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "US"
            phone = poi_html.xpath('.//div[@class="phone"]/a/text()')
            phone = phone[0] if phone else ""
            hoo = loc_dom.xpath(
                '//div[@class="sl-hours border-bottom border-dark-gray"]//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo[1:]) if hoo else ""
            geo = loc_dom.xpath('//a[contains(@href, "maps")]/@href')
            latitude = ""
            longitude = ""
            if geo:
                geo = geo[0].split("/@")[-1].split(",")[:2]
                if len(geo) > 1:
                    latitude = geo[0]
                    longitude = geo[1]

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
