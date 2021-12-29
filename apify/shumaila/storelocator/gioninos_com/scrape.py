import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.gioninos.com/Locations"
    domain = "gioninos.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "locations =")]/text()')[0]
        .split("locations = ")[-1]
        .split(";\r")[0]
    )

    all_locations = json.loads(data)
    for poi in all_locations:
        if not poi["FriendlyUrl"]:
            continue
        page_url = f'https://www.gioninos.com/locations/{poi["FriendlyUrl"]}'
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        street_address = poi["Address1"]
        if poi["Address2"]:
            street_address += " " + poi["Address2"]
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "STORE HOURS:")]/following-sibling::div//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Description"],
            street_address=street_address,
            city=poi["City"],
            state=poi["State"],
            zip_postal=poi["Zip"],
            country_code="",
            store_number=poi["LocationId"],
            phone=poi["Phone"],
            location_type="",
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
