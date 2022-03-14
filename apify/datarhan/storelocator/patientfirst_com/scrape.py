import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "patientfirst.com"
    start_url = "https://www.patientfirst.com/locations-sitemap.xml"

    all_urls = []
    response = session.get(start_url)
    root = etree.fromstring(response.content)
    for sitemap in root:
        children = sitemap.getchildren()
        all_urls.append(children[0].text)

    for store_url in all_urls:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "alternateName")]/text()')[0]
        poi = json.loads(poi.replace("\r\n", ""))
        geo = (
            loc_dom.xpath('//img[@id="mapimage"]/@src')[0]
            .split("center=")[-1]
            .split("&")[0]
            .split(",")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["alternateName"],
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code="",
            store_number="",
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=poi["openingHours"],
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
