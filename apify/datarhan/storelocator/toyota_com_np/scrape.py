import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.com.np/en/contact-us/find-a-dealer.html"
    domain = "toyota.com.np"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "locations_listing")]/text()')[0]
    data = re.findall("locations_listing =(.+);", data.replace("\n", ""))[0]
    data = json.loads(data)

    for poi in data["dealers"]:
        phone = [
            e["numbers"][0]
            for e in poi["contactInfo"]["phoneNos"]
            if e["label"] == "Telephone"
        ][0]
        hoo = []
        for e in poi["openingHours"]["list"]:
            day = e["label"]
            hours = e["time"]
            hoo.append(f"{day} {hours}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=poi["address"]["street"],
            city=poi["address"]["city"],
            state=poi["address"]["state"],
            zip_postal=poi["address"]["postcode"],
            country_code="NP",
            store_number="",
            phone=phone,
            location_type=poi["type"],
            latitude=poi["address"]["lat"],
            longitude=poi["address"]["lng"],
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
