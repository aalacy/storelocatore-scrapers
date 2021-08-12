import re
import ssl
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.bigairusa.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="elementor-icon-list-item"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        city = loc_dom.xpath('//a[contains(@href, "maps")]/span/text()')[-1].split(
            ", "
        )[0]
        state = loc_dom.xpath('//a[contains(@href, "maps")]/span/text()')[-1].split(
            ", "
        )[1]
        location_name = loc_dom.xpath('//a[contains(@href, "maps")]/span/text()')[-1]
        phone = loc_dom.xpath(
            '//span[i[@class="fas fa-mobile-alt"]]/following-sibling::span/text()'
        )[0]
        geo = (
            loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        hoo = loc_dom.xpath('//div[@class="elementor-widget-wrap"]/section[2]//text()')
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[@data-widget_type="uael-business-hours.default"]//text()'
            )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        dir_url = store_url + "direction/"
        loc_response = session.get(dir_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = []
        if loc_response.status_code != 200:
            raw_address = [SgRecord.MISSING, SgRecord.MISSING]
        if not raw_address:
            raw_address = loc_dom.xpath('//h5[contains(text(), "is located")]/text()')
            if raw_address:
                raw_address = raw_address[0].split("located")[-1].strip().split(", ")
        if not raw_address:
            raw_address = loc_dom.xpath('//h5[contains(text(), "ADDRESS:")]/text()')
            if raw_address:
                raw_address = raw_address[0].split("ADDRESS:")[-1].strip().split(", ")
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//p[contains(text(), "shopping center:")]/text()'
            )
            if raw_address:
                raw_address = (
                    raw_address[0].split("shopping center:")[-1].strip().split(", ")
                )
        if not raw_address:
            raw_address = loc_dom.xpath('//p[contains(text(), "is located")]/text()')
            if raw_address:
                raw_address = raw_address[0].split("located")[-1].strip().split(", ")
        if not raw_address:
            with SgChrome() as driver:
                driver.get(dir_url)
                sleep(10)
                driver.switch_to.frame(
                    driver.find_element_by_xpath('//iframe[contains(@src, "google")]')
                )
                loc_dom = etree.HTML(driver.page_source)
                raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0].split(
                    ", "
                )
        street_address = raw_address[0].split("|")[0].replace("at ", "").strip()
        if "Rd Chandler" in street_address:
            street_address = street_address.replace("Rd Chandler", "Rd")
        zip_code = raw_address[-1].split()[-1].replace(".", "")
        if len(zip_code) > 5:
            zip_code = SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=geo[0],
            longitude=geo[-1],
            hours_of_operation=hoo,
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
