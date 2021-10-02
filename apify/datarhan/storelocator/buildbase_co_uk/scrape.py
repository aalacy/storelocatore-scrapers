# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.buildbase.co.uk/storefinder"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall(r"storeLocator.initialize\((.+)\)", response.text)[0][:-7]
    data = json.loads(data)

    all_locations = data["all"]
    for poi in all_locations:
        page_url = f'https://www.buildbase.co.uk/storefinder/store/{poi["ERPSystem"]}-{poi["ID"]}'
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        addr = parse_address_intl(poi["CompleteAddress"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Opening Times")]/following-sibling::ul//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo)
        city = addr.city
        if not city:
            city = poi["CompleteAddress"].split(", ")[-2]
        if street_address.endswith(city):
            street_address = street_address[: -len(city)]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["LocationName"],
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=poi["ID"],
            phone=poi["Phone"],
            location_type=SgRecord.MISSING,
            latitude=poi["Lat"],
            longitude=poi["Lng"],
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
