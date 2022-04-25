from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "fitnessfirst.co.uk"
    start_url = "https://www.fitnessfirst.co.uk/umbraco/surface/location/getregionlocations/?postcode=london&distance=30000"

    data = session.get(start_url).json()
    for poi in data["Locations"]:
        page_url = urljoin(start_url, poi["Url"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = poi["SingleLineAddress"].split(", ")
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Opening Hours")]/following-sibling::dl[1]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Name"],
            street_address=", ".join(raw_address[:-2]),
            city=raw_address[-2],
            state="",
            zip_postal=raw_address[-1],
            country_code="GB",
            store_number=poi["Code"],
            phone=poi["Phone"],
            location_type="",
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
            hours_of_operation=hoo,
            raw_address=poi["SingleLineAddress"],
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
