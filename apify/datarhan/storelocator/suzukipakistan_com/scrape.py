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

    start_url = "https://www.suzukipakistan.com/suzuki-dealers"
    domain = "suzukipakistan.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[@dealer-id]")
    for poi_html in all_locations:
        poi = json.loads(poi_html.xpath(".//input/@value")[0])
        raw_address = poi["SuzukiDealersData"]["DealerAddress"]["Text"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        opens = poi["SuzukiDealersData"]["DealerOpenTiming"]["Value"]
        closes = poi["SuzukiDealersData"]["DealerClosesTiming"]["Value"]
        closed = poi["SuzukiDealersData"]["DealerClosedDays"]["Text"]
        hoo = f"Open: {opens}, Closes {closes}, Close On: {closed}"
        phone = poi["SuzukiDealersData"]["DealerContactNumber"]["Text"]
        if phone:
            phone = (
                phone.split(",")[0].split("/")[0].split(";")[0].split(" - ")[0].strip()
            )
        if phone and len(phone) > 14 and "(" not in phone:
            phone = phone.split()[0]
        city = addr.city
        if city and city.endswith("."):
            city = city[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["TitlePart"]["Title"],
            street_address=street_address,
            city=city,
            state="",
            zip_postal=addr.postcode,
            country_code="Pakistan",
            store_number=poi["SuzukiDealersData"]["DealerCode"]["Text"],
            phone=phone,
            location_type="",
            latitude=poi["GoogleMapPart"]["Lat"],
            longitude=poi["GoogleMapPart"]["Lng"],
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
