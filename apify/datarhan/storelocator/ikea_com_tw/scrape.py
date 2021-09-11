import ssl
from lxml import etree
from urllib.parse import urljoin

from sgselenium.sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com.tw/zh/store/index/"
    domain = "ikea.com.tw"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//strong/a[contains(@href, "/store/")]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url).replace("index", "info")
        loc_response = session.get(page_url)
        if loc_response.status_code != 200:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = loc_dom.xpath('//div[contains(text(), "業時間")]/text()')
        if not raw_data:
            raw_data = loc_dom.xpath('//div[h4[contains(text(), "基本資訊")]]/text()')
        raw_adr = loc_dom.xpath('//p[contains(text(), "地址：")]/text()')
        if raw_adr:
            raw_adr = raw_adr[0].split(":")[-1].strip()
        if not raw_adr and raw_data:
            raw_adr = [e for e in raw_data if "地址" in e][0].split(":")[-1].strip()
            raw_adr = raw_adr.split("：")[-1]
        if not raw_adr:
            with SgChrome() as driver:
                driver.get(page_url)
                driver.switch_to.frame(
                    driver.find_element_by_xpath(
                        "//iframe[@src='https://puop.ikea-event.tw/pc']"
                    )
                )
                loc_dom = etree.HTML(driver.page_source)
                raw_data = loc_dom.xpath('//div[span[@class="info-title"]]/text()')
                raw_adr = [e for e in raw_data if "地址" in e][0].split(":")[-1].strip()

        addr = parse_address_intl(raw_adr)
        location_name = loc_dom.xpath(
            '//div[@class="mb-4 text-wrap bannerTemplate"]/h4/strong/text()'
        )
        location_name = location_name[0] if location_name else ""
        if not location_name:
            location_name = page_url.split("/")[-2].replace("-", " ").title()
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = loc_dom.xpath('//p[contains(text(), "地址：")]/text()')
        phone = phone[1].split("：")[-1].strip().split("按")[0] if phone else ""
        if not phone:
            if raw_data:
                phone = [e for e in raw_data if "電話：" in e]
                phone = phone[0].split("話：")[-1].split("按")[0] if phone else ""
                if not phone:
                    phone = (
                        [e for e in raw_data if "線：" in e][0]
                        .split("：")[-1]
                        .split("轉")[0]
                    )
        if not phone:
            phone = (
                [
                    e
                    for e in loc_dom.xpath('//p[contains(text(), "地址：")]/text()')
                    if "撥：" in e
                ][0]
                .split("撥：")[-1]
                .split()[0]
            )
        hoo = loc_dom.xpath('//h5[contains(text(), "-賣場")]/following::text()')
        hoo = hoo[0].strip() if hoo else ""
        if not hoo:
            if raw_data:
                hoo = [e for e in raw_data if "間：" in e]
                hoo = hoo[0].split("間：")[-1].strip() if hoo else ""
        if not hoo:
            hoo = [
                e
                for e in loc_dom.xpath('//p[contains(text(), "地址：")]/text()')
                if "間：" in e
            ]
            if hoo:
                hoo = hoo[0].split("間：")[-1]
        if hoo == []:
            hoo = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="TW",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_adr,
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
