import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://toyota.iq/en/find-a-dealer/"
    domain = "toyota.iq"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "tiq_dealer")]/text()')[0]
    data = re.findall("tiq_dealers =(.+);", data)[0]
    data = json.loads(data)

    for poi in data["d"]:
        if poi["icon_sale"] != "1":
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=poi["addr"],
            city=poi["city"],
            state="",
            zip_postal="",
            country_code="IQ",
            store_number="",
            phone=poi["tel"],
            location_type="",
            latitude=poi["position"].split(",")[0],
            longitude=poi["position"].split(",")[-1],
            hours_of_operation=poi["hours"],
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
