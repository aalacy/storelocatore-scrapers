from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.com.bh/locations?_format=json"
    domain = "lexus.com.bh"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["nodes"]:
        location_type = poi["node"]["field_branch_type_1"]
        if "Showroom" not in location_type:
            continue
        poi_html = etree.HTML(poi["node"]["body"])
        raw_data = poi_html.xpath("//text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = " ".join(raw_data[:2]).replace("ROAD:", "").replace("\xa0", " ")
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = [e.replace("TEL: ", "") for e in raw_data if "TEL:" in e]
        phone = phone[0] if phone else ""
        geo = poi["node"]["field_longitude"].split(",")
        hoo = [e.replace("OPENING HOURS: ", "") for e in raw_data if "HOURS:" in e]
        hoo = hoo[0] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.lexus.com.bh/store-locator",
            location_name=poi["node"]["title"],
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="BH",
            store_number=poi["node"]["Nid"],
            phone=phone,
            location_type=location_type,
            latitude=geo[0],
            longitude=geo[1],
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
