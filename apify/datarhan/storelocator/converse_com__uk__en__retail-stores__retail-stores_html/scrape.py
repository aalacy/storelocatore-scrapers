from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.converse.com/uk/en/retail-stores/retail-stores.html"
    domain = "onverse.com/uk"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath(
        '//li[@class="content-page"]/div/p[b[contains(text(), "Converse")]]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//b/text()")[0]
        raw_adr = poi_html.xpath("text()")[3:]
        raw_adr = [e.strip() for e in raw_adr]
        addr = parse_address_intl(" ".join(raw_adr))
        country_code = addr.country
        country_code = poi_html.xpath(".//preceding-sibling::h2[1]/b/text()")[0]
        latitude = ""
        longitude = ""
        geo = poi_html.xpath('.//a[contains(@href, "/@")]/@href')
        if geo:
            geo = geo[0].split("@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        city = addr.city
        street_address = raw_adr[0]
        if not city and street_address == "Via della Pace":
            city = "Valmontone"
            street_address += " " + "- Unit 74"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=addr.postcode,
            country_code=country_code,
            store_number="",
            phone="",
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
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
