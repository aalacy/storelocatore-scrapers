# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://gordonsdirect.com/apps/store-locator"
    domain = "gordonsdirect.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="addresses_list"]/ul/li')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//span[@class="name"]/text()')[0].strip()
        street_address = poi_html.xpath('.//span[@class="address"]/text()')[0].strip()
        city = poi_html.xpath('.//span[@class="city"]/text()')[0].strip()
        state = poi_html.xpath('.//span[@class="prov_state"]/text()')[0].strip()
        zip_code = poi_html.xpath('.//span[@class="postal_zip"]/text()')[0].strip()
        store_number = poi_html.xpath("@onfocus")[0].split("Start(")[-1][:-1]
        loc_response = session.get(
            f"https://stores.boldapps.net/front-end/get_store_info.php?shop=gordons-direct.myshopify.com&data=detailed&store_id={store_number}"
        )
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath('.//span[@class="phone"]/text()')[0].strip()
        hoo = loc_dom.xpath('.//span[@class="hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()]).split("**")[0].strip()
        geo = re.findall(r"(lat.+?), id:%s," % store_number, response.text)[0].split(
            "push({"
        )[-1]
        geo = demjson.decode("{" + geo + "}")

        item = SgRecord(
            locator_domain=domain,
            page_url="https://gordonsdirect.com/apps/store-locator",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=geo["lat"],
            longitude=geo["lng"],
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
