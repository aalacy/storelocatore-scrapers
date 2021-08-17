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
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]
        if location_type != "atm":
            continue
        geo = poi["coords"].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hoo = []
        if poi.get("hoursTableHTML"):
            hoo = etree.HTML(poi["hoursTableHTML"]).xpath("//td//text()")
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
