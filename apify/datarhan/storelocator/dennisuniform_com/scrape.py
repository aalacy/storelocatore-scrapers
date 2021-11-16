# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import ssl
from lxml import etree
from time import sleep
from urllib.parse import urljoin

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

    start_url = "https://www.dennisuniform.com/pages/find-a-store"
    domain = "dennisuniform.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[span[contains(text(), "Store Details")]]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        with SgChrome() as driver:
            driver.get(page_url)
            sleep(5)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath("//h1/text()")[0]
            raw_address = loc_dom.xpath(
                '//h2[contains(text(), "Address")]/following-sibling::p/text()'
            )[0].split(", ")
            phone = loc_dom.xpath(
                '//h2[contains(text(), "Phone")]/following-sibling::p/text()'
            )[0]
            hoo = loc_dom.xpath(
                '//h2[contains(text(), "Hours")]/following-sibling::table//text()'
            )
            hoo = " ".join(hoo)
            driver.switch_to.frame(
                driver.find_element(
                    by="xpath",
                    value='//div[@id="map-canvas"]/following-sibling::iframe',
                )
            )
            loc_dom = etree.HTML(driver.page_source)
            geo = (
                loc_dom.xpath('//div[@class="google-maps-link"]/a/@href')[0]
                .split("ll=")[-1]
                .split("&")[0]
                .split(",")
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1],
                state=raw_address[2].split()[0],
                zip_postal=raw_address[2].split()[-1],
                country_code=raw_address[-1],
                store_number="",
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
