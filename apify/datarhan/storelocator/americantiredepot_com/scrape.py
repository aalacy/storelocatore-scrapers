import ssl
from lxml import etree
from urllib.parse import urljoin

from sgselenium import SgChrome
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
    # Your scraper here
    domain = "americantiredepot.com"
    start_url = "https://americantiredepot.com/search/store/locations"

    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        all_locations = dom.xpath('//div[@class="stores-list"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h4/a/@href")[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath(".//h5/text()")
        location_name = location_name[-1].strip() if location_name else "<MISSING>"
        city = poi_html.xpath(".//h4/a/text()")[0]
        if city.split()[-1].isdigit():
            city = city[:-2]
        address_raw = poi_html.xpath('.//p[i[@class="fa fa-map-marker-alt"]]//text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        street_address = " ".join(
            [elem.capitalize() for elem in street_address.split()]
        )
        words = street_address.split()
        street_address = " ".join(sorted(set(words), key=words.index))
        if street_address.endswith(city):
            street_address = street_address.replace(city, "")
        state = address_raw[-1].split()[0]
        zip_code = address_raw[-1].split()[-1]
        phone = poi_html.xpath('.//p[i[@class="fa fa-phone-alt"]]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        if "Coming Soon" in city:
            city = city.split("-")[0].strip()
            location_type = "Coming Soon"
        hours_of_operation = poi_html.xpath(
            './/table[@class="tbl-store-hours mt-2"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
