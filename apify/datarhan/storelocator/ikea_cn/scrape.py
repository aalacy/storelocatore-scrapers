import re
from lxml import etree
from urllib.parse import urljoin

from sgselenium import SgFirefox
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.ikea.cn/cn/en/stores/"
    domain = "ikea.cn"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//a[contains(@href, "/stores/")]/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            if loc_response.url == "https://www.ikea.cn/cn/en/stores/":
                continue
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            if not loc_dom:
                continue

            location_name = loc_dom.xpath('//h1[@class="page-title_head"]/text()')
            if not location_name:
                continue
            location_name = location_name[0].strip()
            raw_adr = loc_dom.xpath(
                '//strong[contains(text(), "Store Address:")]/text()'
            )
            if raw_adr and raw_adr[0] == "Store Address:":
                raw_adr = loc_dom.xpath(
                    '//h4[strong[contains(text(), "Store Address:")]]/text()'
                )
            if raw_adr and raw_adr[0] == "Nantong Store Address:":
                raw_adr = loc_dom.xpath(
                    '//*[strong[contains(text(), "Store Address")]]/following-sibling::p[1]/text()'
                )
            if raw_adr and raw_adr[0] == "Store Address: ":
                raw_adr = loc_dom.xpath(
                    '//strong[contains(text(), "Store Address:")]/following-sibling::strong/text()'
                )
            if raw_adr:
                raw_adr = raw_adr[0].replace("Store Address:", "")
            else:
                raw_adr = loc_dom.xpath(
                    '//*[strong[contains(text(), "Store Address")]]/following-sibling::p[1]/text()'
                )
                if not raw_adr:
                    raw_adr = loc_dom.xpath(
                        '//*[strong[contains(text(), "Store address")]]/following-sibling::p[1]/text()'
                    )
                if not raw_adr:
                    raw_adr = loc_dom.xpath(
                        '//div[h4[strong[contains(text(), "store address")]]]/p/text()'
                    )
                if not raw_adr:
                    raw_adr = loc_dom.xpath(
                        '//h3[contains(text(), "Store Address:")]/text()'
                    )
                raw_adr = raw_adr[0]
            addr = parse_address_intl(raw_adr)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hoo = loc_dom.xpath('//p[contains(text(), "Store Hours:")]/text()')
            if not hoo:
                hoo = loc_dom.xpath('//p[strong[contains(text(), "Store:")]]/text()')
            if not hoo:
                hoo = loc_dom.xpath('//p[contains(text(), "Business Hour:")]/text()')
            if not hoo:
                hoo = loc_dom.xpath('//p[contains(text(), "Store:")]/text()')
            hoo = (
                " ".join(hoo)
                .replace("Store Hours:", "")
                .replace("Store:", "")
                .split("Hour:")[-1]
                .split("Restaurant")[0]
                .strip()
                if hoo
                else ""
            )
            latitude = ""
            longitude = ""
            geo = re.findall(r"&dest=(.+?)\&", loc_response.text)
            if geo:
                geo = geo[0].split(",")
                latitude = geo[1]
                longitude = geo[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                store_number="",
                phone="",
                location_type="",
                latitude=latitude,
                longitude=longitude,
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
