import json
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "theisens.com"
    start_url = "https://www.theisens.com/ProxyRequest.aspx"

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "authorization": "Bearer null",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    formdata = {
        "url": "/api/branchlocator/search/geolocation",
        "data": '{"coordinates":{"latitude":39.4667,"longitude":-0.7167},"range":0,"defaultStoreId":null,"useDefaultLocationIfNoResults":false}',
        "contentType": "application/json",
        "method": "POST",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["results"]:
        store_url = urljoin(start_url, poi["location"]["customUrl"])
        location_name = poi["location"]["locationName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["location"]["address1"]
        if poi["location"]["address2"]:
            street_address += ", " + poi["location"]["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["location"]["city"]
        city = city if city else "<MISSING>"
        state = poi["location"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["location"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["country"]
        store_number = "<MISSING>"
        phone = poi["location"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["latitude"]
        longitude = poi["location"]["longitude"]

        with SgFirefox() as driver:
            driver.get(store_url)
            sleep(5)
            loc_dom = etree.HTML(driver.page_source)
        hoo = loc_dom.xpath('//dd[@id="branch-detail-business-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
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
