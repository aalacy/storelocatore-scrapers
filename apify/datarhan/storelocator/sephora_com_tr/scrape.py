from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.sephora.com.tr/stores/?format=json"
    domain = "sephora.com.tr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["results"]
    for poi in all_locations:
        page_url = urljoin(start_url, poi["absolute_url"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        street_address = poi["address"]
        addr = parse_address_intl(street_address)
        zip_code = addr.postcode
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = poi["township"]["city"]["name"]
        hoo = loc_dom.xpath(
            '//div[@class="store-detail-address-text store-detail-address-hours"]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=zip_code,
            country_code=poi["township"]["city"]["country"]["code"],
            store_number=poi["pk"],
            phone=poi["phone_number"],
            location_type=poi["store_type"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
