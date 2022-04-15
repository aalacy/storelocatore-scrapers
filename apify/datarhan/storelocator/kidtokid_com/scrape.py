from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "kidtokid.com"
    start_url = "https://kidtokid.com/stores/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[span[contains(text(), "View Location")]]/@href')
    all_states = dom.xpath('//a[contains(@href, "search-results")]/@href')
    for url in all_states:
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[span[contains(text(), "View Location")]]/@href')

    for url in list(set(all_locations)):
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//div[contains(text(), "coming soon")]'):
            continue

        location_name = " ".join(
            loc_dom.xpath(
                '//div[@class="elementor-column-wrap elementor-element-populated"]//h1/text()'
            )
        )
        raw_address = loc_dom.xpath(
            '//div[div[h2[contains(text(), "Contact Us")]]]/following-sibling::div//p/text()'
        )
        if not raw_address:
            continue
        country_code = "US"
        zip_code = " ".join(raw_address[1].split(", ")[-1].split()[1:])
        if len(zip_code.split()) == 2:
            country_code = "CA"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/span/text()')[0]
        hoo = loc_dom.xpath(
            '//div[div[h2[contains(text(), "Store Hours")]]]/following-sibling::div//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
