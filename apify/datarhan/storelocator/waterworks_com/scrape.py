import json
from lxml import etree
from time import sleep
from random import uniform

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(proxy_country="us", verify_ssl=False)
    domain = "waterworks.com"
    start_url = "https://www.waterworks.com/us_en/storelocation/index/storelist/"

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    formdata = {"agIds[]": "1"}
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["storesjson"]:
        store_url = "https://www.waterworks.com/us_en/{}".format(
            poi["rewrite_request_path"]
        )
        hdr = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        }
        loc_response = session.get(store_url, headers=hdr)
        denied = True if loc_response.status_code != 200 else False
        while denied:
            sleep(uniform(5, 15))
            session = SgRequests(proxy_country="us")
            loc_response = session.get(store_url, headers=hdr)
            denied = True if loc_response.status_code != 200 else False
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["store_name"]
        street_address = poi["address"]
        if "@" in street_address:
            street_address = ""
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zipcode"]
        country_code = poi["country_id"]
        store_number = poi["storelocation_id"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = loc_dom.xpath(
            '//dt[contains(text(), "Hours")]/following-sibling::dd//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

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
