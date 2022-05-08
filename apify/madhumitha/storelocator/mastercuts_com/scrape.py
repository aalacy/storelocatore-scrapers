from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox

start_url = "https://www.signaturestyle.com/salon-directory.html"
domain = "mastercuts.com"
hdr = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
}

driver = SgFirefox().driver()


def get_driver(retry=0):
    global driver
    if retry:
        driver = SgFirefox().driver()

    return driver


def fetch_location(poi_html, retry=0):
    try:
        url = poi_html.xpath("@href")[0]
        raw_address = poi_html.xpath("text()")[0]
        page_url = urljoin(start_url, url)
        driver.get(page_url)
        loc_dom = etree.HTML(driver.page_source)

        location_name = loc_dom.xpath("//h2/text()")
        if not location_name:
            return None
        location_name = location_name[0]
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else ""
        if not street_address:
            street_address = raw_address.split(", ")[1]
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else ""
        if not city:
            city = raw_address.split(", ")[2]
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else ""
        if not state:
            state = raw_address.split(", ")[3].split()[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else ""
        if not zip_code:
            zip_code = raw_address.split(", ")[3].split()[1]
        phone = loc_dom.xpath('//a[@id="sdp-phone"]/text()')
        phone = phone[0] if phone else ""
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        if not latitude:
            return None
        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath(
            '//div[@class="salondetailspagelocationcomp"]//div[@class="store-hours sdp-store-hours"]//text()'
        )
        hoo = " ".join(hoo).split(" Monday")[0]
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="salon-timings"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
        )

        return item
    except:
        if retry < 3:
            return fetch_location(poi_html, retry + 1)


def fetch_data():
    session = SgRequests()

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//a[@class="btn btn-primary"]/@href')
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations = dom.xpath("//td/a")
        for poi_html in all_locations:
            poi = fetch_location(poi_html)
            if poi:
                yield poi


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
