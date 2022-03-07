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

    start_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/4482/stores.js?callback=SMcallback2"
    domain = "milanlaser.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr)
    data = json.loads(data.text.split("back2(")[-1][:-1])

    all_locations = data["stores"]
    for poi in all_locations:
        page_url = poi["url"]
        page_url = page_url.replace("http://htttps://", "https://")
        loc_response = session.get(page_url + "/about-us/", headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = poi["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        hoo = loc_dom.xpath(
            '//h5[contains(text(), "Hours of Operation")]/following-sibling::p[1]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split(" (S")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
