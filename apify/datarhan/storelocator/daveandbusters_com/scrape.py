import re
import json
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "daveandbusters.com"
    start_url = "https://www.daveandbusters.com/locations"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-list-item"]//a/@href')
    for url in list(set(all_locations)):
        page_url = urljoin(start_url, url)
        response = session.get(page_url, headers=hdr)
        dom = etree.HTML(response.text)
        loc_id = re.findall(r"AddLocationId\((\d+)\);", response.text)
        try:
            response = session.get(
                "https://www.daveandbusters.com/umbraco/api/LocationDataApi/GetLocationDataById?locationId={}".format(
                    loc_id[0]
                ),
                headers=hdr,
            )
        except Exception:
            response = session.get(
                "https://www.daveandbusters.com/umbraco/api/LocationDataApi/GetLocationSpecialDataById?locationId={}".format(
                    loc_id[0]
                ),
                headers=hdr,
            )
        if response.status_code != 200:
            continue

        poi = json.loads(response.text)
        hours_of_operation = poi["YextData"]["Hours"]["StoreHours"]
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""
        location_type = ""
        if poi["TempClosed"]:
            hours_of_operation = ""
            location_type = "temporary closed"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["DisplayName"],
            street_address=poi["Address"],
            city=poi["City"],
            state=poi["State"],
            zip_postal=poi["Zip"],
            country_code=poi["Country"],
            store_number=poi["ID"],
            phone=poi["Phone"],
            location_type=location_type,
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
