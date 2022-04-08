import re
import json
from lxml import etree
from sglogging import sglog
from urllib.parse import urljoin
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

DOMAIN = "pgatoursuperstore.com"
BASE_URL = "https://www.pgatoursuperstore.com/stores"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_data():
    session = SgRequests()
    domain = re.findall(r"://(.+?)/", BASE_URL)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(BASE_URL, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="store"]')
    for poi_html in all_locations:
        url = poi_html.xpath('.//div[@class="storename"]/a/@href')[0]
        store_url = urljoin(BASE_URL, url)
        loc_response = session.get(store_url)
        try:
            loc_dom = etree.HTML(loc_response.text)
        except:
            continue
        poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
        poi = json.loads(poi)

        location_name = poi_html.xpath('.//div[@class="storename"]/a/span/text()')[0]
        street_address = poi_html.xpath('.//div[@class="address1"]/text()')[0]
        adr_2 = poi_html.xpath('.//div[@class="address2"]/text()')
        if adr_2:
            street_address += " " + adr_2[0]
        raw_address = poi_html.xpath('.//div[@class="cityStateZip"]/text()')[0].split(
            ", "
        )
        phone = poi_html.xpath('.//div[@class="phone"]/a/text()')
        phone = phone[0] if phone else SgRecord.MISSING
        hoo = poi_html.xpath('.//div[@class="hours"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo)
        location_type = SgRecord.MISSING
        if "Temporarily closed" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Temporarily closed")[0]
            location_type = "Temporarily closed"
        if "Coming" in location_name:
            continue
        log.info("Append {} => {}".format(location_name, street_address))
        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=raw_address[0],
            state=raw_address[1].split()[0],
            zip_postal=raw_address[1].split()[-1],
            country_code="US",
            store_number=store_url.split("/")[-1].split(".")[0],
            phone=phone,
            location_type=location_type,
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
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
