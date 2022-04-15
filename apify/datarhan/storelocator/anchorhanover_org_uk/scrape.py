import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://www.anchorhanover.org.uk/our-properties/locations"
    domain = "anchorhanover.org.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = []
    all_counties = dom.xpath(
        '//h4[contains(text(), "Select a county")]/following-sibling::ul[1]//a/@href'
    )
    for url in all_counties:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath(
            '//h3[contains(text(), "Care homes")]/following-sibling::ul[1]//a/@href'
        )
        for url in all_cities:
            url = urljoin(start_url, url)
            response = session.get(url, headers=hdr)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath(
                '//a[@class="property-results__nested-link"]/@href'
            )
            all_locations += dom.xpath(
                '//div[@class="property-results__buttons"]/a/@href'
            )

    for page_url in all_locations:
        page_url = urljoin(start_url, page_url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')[0]
        poi = json.loads(poi)
        location_type = loc_dom.xpath(
            '//button[contains(text(), "Property type")]/following-sibling::div[1]/p/text()'
        )[0]
        geo = (
            loc_dom.xpath('//iframe[contains(@src, "/maps/embed")]/@src')[0]
            .split("q=")[-1]
            .split(",")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["@graph"][2]["name"],
            street_address=poi["@graph"][2]["address"]["streetAddress"],
            city=poi["@graph"][2]["address"]["addressLocality"],
            state=poi["@graph"][2]["address"]["addressRegion"],
            zip_postal=poi["@graph"][2]["address"]["postalCode"],
            country_code="",
            store_number="",
            phone=poi["@graph"][2]["telephone"],
            location_type=location_type,
            latitude=geo[0],
            longitude=geo[1],
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
