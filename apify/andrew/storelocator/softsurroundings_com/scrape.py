import ssl
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

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

    start_url = "https://www.softsurroundings.com/stores/all/"
    domain = "softsurroundings.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "visit store page")]/@href')
    with SgChrome() as driver:
        for url in all_locations:
            page_url = urljoin(start_url, url)
            driver.get(page_url)
            sleep(10)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath('//h2[@class="sans storeName"]/text()')[0]
            raw_data = loc_dom.xpath('//ul[@class="storeList"]/li/text()')
            phone = loc_dom.xpath('//li[img[@class="phoneicon"]]/text()')
            phone = phone[0] if phone else ""
            store_number = loc_dom.xpath('//input[@id="storeId"]/@value')[0]
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps/@")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            hoo = loc_dom.xpath(
                '//h4[contains(text(), "Store Hours:")]/following-sibling::p[1]//text()'
            )
            hoo = (
                " ".join([e.strip() for e in hoo if e.strip()])
                .replace("\xa0", " ")
                .split("order. ")[-1]
                .strip()
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_data[0],
                city=raw_data[1].split(", ")[0],
                state=raw_data[1].split(", ")[-1].split()[0],
                zip_postal=raw_data[1].split(", ")[-1].split()[1],
                country_code="",
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
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
