import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://locations.expresscare.com/"
    domain = "expresscare.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_sates = dom.xpath('//a[@data-gaact="Click_to_State"]/@href')
    for url in all_sates:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//a[@data-gaact="Click_to_City_Page"]/@href')
        for url in all_cities:
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//a[@data-gaact="Click_to_Store_Page"]/@href')
            for page_url in all_locations:
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)
                poi = loc_dom.xpath(
                    '//script[contains(text(), "addressRegion")]/text()'
                )[0]
                poi = json.loads(poi)
                hoo = []
                for e in poi["openingHoursSpecification"]:
                    day = e["dayOfWeek"][0]
                    hoo.append(f'{day} {e["opens"]} - {e["closes"]}')
                hoo = " ".join(hoo)

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=poi["address"]["postalCode"],
                    country_code=poi["address"]["addressCountry"],
                    store_number=poi["@id"],
                    phone=poi["telephone"],
                    location_type=poi["@type"],
                    latitude=poi["geo"]["latitude"],
                    longitude=poi["geo"]["longitude"],
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
