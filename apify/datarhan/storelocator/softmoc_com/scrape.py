import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_urls = [
        "https://www.softmoc.com/ca/locations.aspx",
        "https://www.softmoc.com/us/locations.aspx",
    ]
    domain = "softmoc.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)
        data = dom.xpath('//script[contains(text(), "var locations")]/text()')[1]
        data = re.findall(r"var locations2 =(.+?\]);", data.replace("\n", ""))[0]
        data = demjson.decode(data)

        for poi in data:
            if "/ca/" in start_url:
                store_url = (
                    "https://www.softmoc.com/ca/locations/" + poi["details"]["storeUrl"]
                )
            else:
                store_url = (
                    "https://www.softmoc.com/us/locations/" + poi["details"]["storeUrl"]
                )
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi["details"]["name"]
            street_address = poi["details"]["address"]
            city = poi["details"]["city"]
            state = poi["details"]["state"]
            zip_code = poi["details"]["zip"]
            country_code = poi["details"]["country"]
            store_number = poi["details"]["id"]
            phone = poi["details"]["phone"]
            phone = phone if phone else "<MISSING>"
            latitude = poi["lat"]
            longitude = poi["lng"]
            hoo = loc_dom.xpath('//table[@class="store-hours w-full"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
                location_type=SgRecord.MISSING,
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
