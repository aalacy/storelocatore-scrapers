import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.cityelectricsupply.com/branchLocator"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall("jsonAllBranches = (.+);", response.text)[0]
    all_locations = json.loads(data)

    for poi in all_locations:
        store_url = "https://www.cityelectricsupply.com/branch/" + poi["BranchId"]
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        street_address = poi["Address1"]
        if poi["Address2"]:
            street_address += " " + poi["Address2"]
        hoo = loc_dom.xpath('//ul[@class="col-12 branch-store-hours-details"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=SgRecord.MISSING,
            location_name=poi["BranchName"],
            street_address=street_address,
            city=poi["City"],
            state=poi["State"],
            zip_postal=poi["ZipCode"],
            country_code=SgRecord.MISSING,
            store_number=poi["BranchId"],
            phone=poi["Phone"],
            location_type=SgRecord.MISSING,
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
