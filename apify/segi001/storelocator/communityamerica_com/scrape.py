from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = (
        "https://www.communityamerica.com/api/locator?lat=39.099719&lng=-94.578955"
    )
    domain = "communityamerica.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    with SgRequests() as session:
        all_locations = session.get(start_url, headers=hdr).json()
        for poi in all_locations:
            street_address = poi["address"]["street"]
            if poi["address"]["street2"]:
                street_address += ", " + poi["address"]["street"]
            hoo = []
            page_url = "https://www.communityamerica.com/locations"
            if poi.get("link"):
                page_url = urljoin(start_url, poi["link"])
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)
                hoo = loc_dom.xpath(
                    '//h5[contains(text(), "Lobby Hours")]/following-sibling::ul//text()'
                )
                hoo = " ".join([e.strip() for e in hoo])

            if len(hoo) <= 0:
                hoo = SgRecord.MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["address"]["city"],
                state=poi["address"]["state"],
                zip_postal=poi["address"]["zip"],
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=poi.get("phone"),
                location_type=poi["locatorType"],
                latitude=poi["address"]["latitude"],
                longitude=poi["address"]["longitude"],
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
