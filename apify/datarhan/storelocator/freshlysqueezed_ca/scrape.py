import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "http://www.freshlysqueezed.ca/stores/"
    domain = "reshlysqueezed.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="azt_frontend-js-extra"]/text()')[0]
    data = re.findall(" azt =(.+);", data)[0]
    data = json.loads(data)
    all_locations = data["table"]
    for poi in all_locations:
        hoo = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hoo_data = json.loads(poi["working_hours"])
        for i, e in enumerate(hoo_data):
            hoo.append(f'{days[i]}: {e["p"][0]["f"]} - {e["p"][0]["t"]}')
        hoo = " ".join(hoo)
        addr = parse_address_intl(poi["street"])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["title"],
            street_address=poi["street"].split(", ")[0],
            city=poi["city"],
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
