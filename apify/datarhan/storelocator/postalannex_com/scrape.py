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
    all_locations = dom.xpath('//a[div[contains(text(), "Visit Website")]]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        r_loc = session.get(store_url, headers=headers)
        loc_dom = html.fromstring(r_loc.text, "lxml")
        if loc_dom.xpath('//div[contains(text(), "Coming Soon")]'):
            continue
        location_name = loc_dom.xpath('//div[@id="views_title"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[1] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = store_url.split("/")[-1]
        phone = loc_dom.xpath('//a[@id="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//meta[@name="geo.position"]/@content')
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[0].split(";")
            latitude = geo[0]
            longitude = geo[1]
        hoo = loc_dom.xpath('//div[@id="block-store-hours-block"]/div/div/text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
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
