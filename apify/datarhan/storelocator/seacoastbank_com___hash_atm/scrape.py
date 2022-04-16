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
        store_url = "<MISSING>"
        if poi["detailsURL"]:
            store_url = "https://www.seacoastbank.com" + poi["detailsURL"]
        location_name = poi["name"]
        street_address = poi["streetAddress"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        phone = poi["phone"]
        location_type = poi["type"]
        geo = poi["coords"].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hoo = []
        if poi.get("hoursTableHTML"):
            hours = []
            hours = etree.HTML(poi["hoursTableHTML"]).xpath("//tr")
            for e in hours:
                hoo.append(" ".join(e.xpath(".//text()")[:-1]))
        hours_of_operation = (
            " ".join(hoo).replace("N/A", "").replace("Lobby ", "") if hoo else ""
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
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
