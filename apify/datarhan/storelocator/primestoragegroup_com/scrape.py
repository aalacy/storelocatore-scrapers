import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.primestoragegroup.com/self-storage/"
    domain = "primestoragegroup.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[@data-lat]")
    next_page = dom.xpath('//a[@class="next page-link"]/@href')
    while next_page:
        response = session.get(next_page[0], headers=hdr)
        dom = etree.HTML(response.text)

        all_locations += dom.xpath("//div[@data-lat]")
        next_page = dom.xpath('//a[@class="next page-link"]/@href')

    for poi_html in all_locations:
        page_url = poi_html.xpath(
            './/div[@class="fs-1-5 font-weight-bold mt-2"]/a/@href'
        )[0]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[@class="yoast-schema-graph"]/text()')[0]
        poi = json.loads(poi)
        phone = poi["@graph"][0]["telephone"]
        if not phone:
            phone = loc_dom.xpath('//address/a[contains(@href, "tel")]/text()')[0]
        hoo = poi["@graph"][0].get("openingHours")
        if not hoo:
            hoo = loc_dom.xpath('//div[@id="hours-popper"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("Access Hours:")[-1].strip()
        if "sa " not in hoo:
            hoo += " sa closed"
        if "su " not in hoo:
            hoo += " su closed"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["@graph"][0]["name"],
            street_address=poi["@graph"][0]["address"]["streetAddress"],
            city=poi["@graph"][0]["address"]["addressLocality"],
            state=poi["@graph"][0]["address"]["addressRegion"],
            zip_postal=poi["@graph"][0]["address"]["postalCode"],
            country_code=poi["@graph"][0]["address"]["addressCountry"],
            store_number="",
            phone=phone,
            location_type=poi["@graph"][0]["@type"][-1],
            latitude=poi["@graph"][0]["geo"]["latitude"],
            longitude=poi["@graph"][0]["geo"]["longitude"],
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
