import re
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.nationalwindscreens.co.uk/fitting-centres"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "fittingCentres")]/text()')[0]
    data = re.findall("fittingCentres =(.+);", data)[0]

    all_locations = json.loads(data)
    for poi in all_locations:
        page_url = urljoin(start_url, poi["slug"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        street_address = f"{poi['address']['line1']} {poi['address']['line2']} {poi['address']['line3']}"
        city = poi["address"]["town"]
        street_address = street_address.split(city)[0].strip()
        hoo = loc_dom.xpath('//div[@class="opening-hours"]//ul//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"]["shortAddress"],
            city=city,
            state=poi["address"]["county"],
            zip_postal=poi["address"]["postcode"],
            country_code=poi["address"]["country"],
            store_number=poi["id"],
            phone=poi["tel"],
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lng"],
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
