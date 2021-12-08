from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://toyota.com.ph/get-dealers-by-area-id-limit/{}?page=1"
    domain = "toyota.com.ph"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get("https://toyota.com.ph/dealer", headers=hdr)
    dom = etree.HTML(response.text)
    all_regions = dom.xpath('//select[@id="select-area"]/option/@value')[1:]
    for region in all_regions:
        data = session.get(start_url.format(region), headers=hdr).json()
        all_locations = data["data"]
        while data["next_page_url"]:
            data = session.get(data["next_page_url"], headers=hdr).json()
            all_locations += data["data"]

        for poi in all_locations:
            addr = parse_address_intl(poi["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url="https://toyota.com.ph/dealer",
                location_name=poi["name"],
                street_address=street_address,
                city=addr.city,
                state="",
                zip_postal=addr.postcode,
                country_code="PH",
                store_number=poi["code"],
                phone=poi["contacts"][0]["contact_number"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation="",
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
