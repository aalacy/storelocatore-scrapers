import json
from lxml import etree
from w3lib.html import remove_tags

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "davidsbridal.com"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    start_url = "https://www.davidsbridal.com/DBIStoresDirectoryView?catalogId=10051&langId=-1&storeId=10052"
    response = session.post(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_poi_urls = dom.xpath('//a[@class="store-address1"]/@href')
    for store_url in all_poi_urls:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        store_data = (
            loc_dom.xpath('//script[contains(text(), "longitude")]/text()')[0]
            .replace(' style="color:black;"', "")
            .replace('style="color:red;"', "")
        )
        store_data = json.loads(store_data)

        location_name = store_data["name"]
        street_address = store_data["address"]["streetAddress"]
        city = store_data["address"]["addressLocality"]
        state = store_data["address"]["addressRegion"]
        zip_code = store_data["address"]["postalCode"]
        country_code = store_data["address"]["addressCountry"]
        phone = store_data["telephone"]
        location_type = store_data["@type"]
        latitude = store_data["geo"]["latitude"]
        longitude = store_data["geo"]["longitude"]
        hours_of_operation = "M-F: {}, Sat: {}, Sun: {}".format(
            store_data["openingHours"][0],
            store_data["openingHours"][1],
            store_data["openingHours"][2],
        )
        hours_of_operation = remove_tags(hours_of_operation)

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
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
