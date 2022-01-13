import ssl
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    session = SgRequests(verify_ssl=False)
    start_url = "https://www.elcorteingles.pt/info/centros/"
    domain = "elcorteingles.pt"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    with SgChrome() as driver:
        driver.get(start_url)
        sleep(15)
        all_locations = driver.find_elements_by_xpath('//div[@class="map-responsive"]')
        for elem in all_locations:
            driver.switch_to.frame(
                elem.find_element_by_xpath('.//iframe[contains(@src, "maps")]')
            )
            loc_dom = etree.HTML(driver.page_source)
            raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0].split(", ")
            geo = (
                loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            driver.switch_to.default_content()
            location_name = city = raw_address[1].split()[-1].strip()
            hoo = dom.xpath(
                '//p[strong[contains(text(), "{}")]]/following-sibling::p[1]/text()'.format(
                    city.upper()
                )
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=city,
                state="",
                zip_postal=raw_address[1].split()[0],
                country_code=raw_address[-1],
                store_number="",
                phone="",
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
