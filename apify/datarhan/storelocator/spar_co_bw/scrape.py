from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.spar.co.za/api/stores/search"
    domain = "spar.co.bw"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }
    frm = {
        "ProvinceId": "14",
        "SearchText": "",
        "Types": ["SPAR", "SUPERSPAR"],
        "Services": [],
    }
    all_locations = session.post(start_url, headers=hdr, json=frm).json()
    for poi in all_locations:
        page_url = f'https://www.spar.co.za/Store-View-Frame/{poi["Alias"]}'
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = f'{poi["PhysicalAddress"]}, {poi["Suburb"]}, {poi["Town"]}'
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        hoo = loc_dom.xpath('//ul[@class="si-hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        country_code = ""
        if "Botswana" in page_url:
            country_code = "Botswana"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=country_code,
            store_number=poi["Id"],
            phone=poi["TelephoneNumber"],
            location_type=poi["Type"],
            latitude=poi["GPSLat"],
            longitude=poi["GPSLong"],
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
