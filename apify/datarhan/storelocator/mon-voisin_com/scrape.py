import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "mon-voisin.com"
    start_url = "https://www.mon-voisin.com/en/store-locator/"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "store-result")]')
    for poi_html in all_locations:
        page_url = poi_html.xpath(".//h4/a/@href")[0]
        page_url = urljoin(start_url, page_url)
        location_name = poi_html.xpath('.//span[@class="name"]/text()')[0]
        street_address = poi_html.xpath(
            './/span[@class="location_address_address_1"]/text()'
        )[0]
        city = poi_html.xpath('.//span[@class="city"]/text()')[0]
        state = poi_html.xpath('.//span[@class="province"]/text()')[0]
        zip_code = poi_html.xpath('.//span[@class="postal_code"]/text()')[0]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        store_number = poi_html.xpath("@data-id")[0]
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]
        hoo_data = json.loads(poi_html.xpath("@data-hours")[0].replace("\\u00e0", "-"))
        hoo = []
        for day, hours in hoo_data.items():
            if not hours:
                continue
            hoo.append(f"{day}: {hours}")
        hoo = " ".join(hoo)
        if not hoo:
            loc_response = session.get(page_url, headers=headers)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath(
                '//h3[contains(text(), "Store Hours")]/following-sibling::h4/text()'
            )
            hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
