from lxml import html
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "postalannex.com"
    start_url = "https://www.postalannex.com/locations"

    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }
    response = session.get(start_url, headers=headers)
    dom = html.fromstring(response.text)
    all_locations = dom.xpath('//div[@class=" blockish address-list"]')
    for poi_html in all_locations:
        url = poi_html.xpath(".//a/@href")[0]
        store_url = urljoin(start_url, url)
        r_loc = session.get(store_url, headers=headers)
        if r_loc.status_code != 200:
            continue
        loc_dom = html.fromstring(r_loc.text, "lxml")
        if loc_dom.xpath('//div[contains(text(), "Coming Soon")]'):
            continue
        location_name = poi_html.xpath('.//div[@class="storename"]/a/text()')
        location_name = location_name[0] if location_name else ""
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = " ".join(street_address) if street_address else ""
        if not street_address:
            street_address = poi_html.xpath('.//div[@class="loc-sub"]/a/text()')[0]
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else ""
        if not city:
            city = poi_html.xpath('.//div[@class="loc-sub"]/text()')[0].split(", ")[0]
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else ""
        if not state:
            state = (
                poi_html.xpath('.//div[@class="loc-sub"]/text()')[0]
                .split(", ")[-1]
                .split()[0]
            )
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[1] if zip_code else ""
        if not zip_code:
            zip_code = (
                poi_html.xpath('.//div[@class="loc-sub"]/text()')[0]
                .split(", ")[-1]
                .split()[-1]
            )
        store_number = store_url.split("/")[-1]
        phone = loc_dom.xpath('//a[@id="phone"]/text()')
        phone = phone[0] if phone else ""
        if not phone:
            phone = poi_html.xpath('.//div[@class="loc-sub"]/a/text()')[-1]
        geo = loc_dom.xpath('//meta[@name="geo.position"]/@content')
        if geo:
            geo = geo[0].split(";")
            latitude = geo[0]
            longitude = geo[1]
        hoo = loc_dom.xpath('//div[@id="block-store-hours-block"]/div/div/text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
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
