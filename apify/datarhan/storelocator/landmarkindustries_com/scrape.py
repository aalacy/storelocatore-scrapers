from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_usa


def fetch_data():
    session = SgRequests()
    domain = "landmarkindustries.com"
    start_url = "https://www.landmarkindustries.com/retail.htm"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//td[@width="263"]/p/text()')
    all_locations_raw = "".join(all_locations).split("\r\n")
    all_poi = []
    for elem in all_locations_raw:
        all_poi += elem.strip().split("\n")
    all_poi = [e.strip() for e in all_poi if e.strip()]

    for poi_data in all_poi:
        raw_address = " ".join(poi_data.split("/")[1].replace("Exxon", "").split()[:-1])
        addr = parse_address_usa(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi_data.split("/")[0],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number=poi_data.split("-")[0],
            phone=poi_data.split()[-1],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
