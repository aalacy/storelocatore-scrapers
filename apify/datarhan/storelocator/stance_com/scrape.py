from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.stance.com/retail"
    domain = "stance.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    outlet_stores = dom.xpath(
        '//h1[contains(text(), "Outlet Stores")]/following-sibling::div[1]/div[@class="store-card"]'
    )
    retail_stores = dom.xpath(
        '//h1[contains(text(), "Stance Stores")]/following-sibling::div[1]/div[@class="store-card"]'
    )
    all_stores = {"outlet": outlet_stores, "retail": retail_stores}
    for location_type, all_locations in all_stores.items():
        for poi_html in all_locations:
            page_url = poi_html.xpath('.//div[@class="store-info"]/div/a/@href')[0]
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath('//p[@class="address"]/text()')
            raw_address = [e.strip() for e in raw_address if e.strip()]
            hoo = loc_dom.xpath('//div[@class="row hours"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)
            phone = loc_dom.xpath('//p[@class="phone"]/text()')
            phone = phone[0] if phone else ""
            country_code = raw_address[-1] if len(raw_address) == 3 else ""
            location_name = "STANCE Outlet"
            if location_type == "retail":
                location_name = "STANCE Store"

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1].split(", ")[0],
                state=raw_address[1].split(", ")[-1].split()[0],
                zip_postal=raw_address[1].split(", ")[-1].split()[-1],
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type=location_type,
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
