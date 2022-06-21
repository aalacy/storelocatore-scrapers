import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "seacoastbank.com"
    start_url = "https://www.seacoastbank.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    data = (
        dom.xpath('//script[@id="marker-data"]/text()')[0]
        .split("markers =")[-1]
        .strip()[:-1]
    )
    data = re.sub(r"new google.maps.LatLng\((.+?)\)", r'"\1"', data.replace("\n", ""))
    all_locations = demjson.decode(data)

    for poi in all_locations:
        page_url = start_url
        if poi["detailsURL"]:
            page_url = "https://www.seacoastbank.com" + poi["detailsURL"]
        phone = poi["phone"]
        if not phone:
            continue
        location_type = poi["type"]
        if location_type == "atm":
            continue
        geo = poi["coords"].split(",")
        latitude = geo[0]
        longitude = geo[1]

        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath(
            '//div[div[div[contains(text(), "LOBBY HOURS")]]]/following-sibling::div[1]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["streetAddress"],
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["zip"],
            country_code="",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
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
