import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    # Your scraper here
    session = SgRequests()
    domain = "pharmaprix.ca"
    start_url = "https://stores.pharmaprix.ca/en/province/qc/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.post(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_poi = dom.xpath('//div[@class="col-sm-6 col-md-3 listing-link"]/a/@href')
    for store_url in all_poi:
        print(store_url)
        store_response = session.get(store_url)
        data = re.findall("model=(.+?)>", store_response.text)[0][1:-1]
        data = data.replace("&quot;", '"')
        data = json.loads(data)
        poi = data["storeDetails"]["store"]

        location_name = poi["name"]
        street_address = poi["address"]
        city = poi["city"]
        state = poi["province"]["abbreviation"]
        zip_code = poi["postalCode"]
        store_number = store_url.split("/")[-2]
        phone = poi["phone"]
        location_type = poi["storeType"]["displayName"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours = poi["storeHours"]
        days = poi["weekDays"]
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
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
