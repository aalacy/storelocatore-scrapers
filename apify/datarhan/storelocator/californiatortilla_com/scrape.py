import re
import yaml
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    domain = "californiatortilla.com"
    start_url = "https://www.californiatortilla.com/locations/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "locations = ")]/text()')[0]
    data = re.findall("locations =(.+);", data.replace("\n", ""))
    data = (
        data[0]
        .replace("new google.maps.LatLng(", "")
        .replace("),\t", ",")
        .replace("\t", "")
    )
    data = yaml.load(data)

    for poi in data:
        store_url = poi["url"]
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath(
            '//span[contains(text(), "Address")]/following-sibling::p[1]/text()'
        )
        raw_address = [elem.strip() for elem in raw_address]

        location_name = (
            poi["name"]
            .replace("&#8211;", "")
            .replace(" &#038;", "")
            .replace("&#8217;", "'")
        )
        location_name = location_name if location_name else SgRecord.MISSING
        street_address = poi["street"].replace(" &#038;", "").replace("&#8217;", "'")
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = poi["zip"]
        store_number = poi["id"]
        latitude = poi["coords"].split(",")[0]
        longitude = poi["coords"].split(",")[1]
        phone = poi["phone"]
        phone = phone if phone else SgRecord.MISSING
        hoo = loc_dom.xpath(
            '//span[contains(text(), "Hours")]/following-sibling::p/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).replace("\n", "").replace("\t", "")
            if hoo
            else SgRecord.MISSING
        )

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
